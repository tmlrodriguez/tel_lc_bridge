from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LoanRepaymentBridge(models.Model):
    _inherit = 'loan.manager.repayment'

    internal_payment = fields.Boolean(string='Pago Interno', help="Marcar si el pago se realizará con un retiro interno.", default=False)
    withdrawal_id = fields.Many2one('contributions.manager.withdrawal', string='Retiro Asociado', domain="[('partner_id', '=', loan_id.partner_id), ('internal_use', '=', True), ('withdrawal_status', '=', 'registered'), ('internal_used', '=', False)]", help="Seleccionar el retiro de uso interno registrado disponible para cruzar con esta cuota.")

    def write(self, vals):
        base_allowed = {'status', 'move_id', 'payment_date', 'amount_paid'}
        bridge_allowed = {'withdrawal_id', 'internal_payment'}
        allowed = base_allowed | bridge_allowed
        illegal = set(vals.keys()) - allowed
        if illegal:
            raise ValidationError(
                "Las cuotas no se pueden editar manualmente. "
                f"Campos no permitidos: {', '.join(sorted(illegal))}"
            )
        return models.Model.write(self, vals)

    @api.onchange('withdrawal_id')
    def _onchange_withdrawal_id(self):
        if self.withdrawal_id:
            self.amount_paid = self.withdrawal_id.amount


class LoanRepaymentConfirmBridge(models.TransientModel):
    _inherit = 'loan.manager.repayment.confirm.wizard'

    repayment_partner_id = fields.Many2one('res.partner', string='Cliente (helper)', readonly=True)
    internal_payment = fields.Boolean(string='Pago Interno')
    withdrawal_id = fields.Many2one('contributions.manager.withdrawal', string='Retiro Interno', help='Seleccionar el retiro interno registrado disponible para cruzar con esta cuota.')
    _previous_partial_amount = fields.Float(string='Monto Previo', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        repayment = self.env['loan.manager.repayment'].browse(self.env.context.get('active_id'))
        if repayment:
            res['repayment_partner_id'] = repayment.loan_id.partner_id.id or False
        return res

    @api.onchange('repayment_id')
    def _onchange_repayment_id_set_partner(self):
        self.repayment_partner_id = self.repayment_id.loan_id.partner_id

    @api.onchange('internal_payment')
    def _onchange_internal_payment(self):
        if self.internal_payment:
            self._previous_partial_amount = self.partial_amount or self.total_to_pay
            self.partial_amount = 0.0
        else:
            self.partial_amount = self._previous_partial_amount or self.total_to_pay
            self.withdrawal_id = False

    @api.onchange('withdrawal_id')
    def _onchange_withdrawal_id(self):
        if self.withdrawal_id:
            self.partial_amount = self.withdrawal_id.amount

    def action_confirm(self):
        res = super().action_confirm()
        if self.internal_payment and self.withdrawal_id:
            withdrawal = self.withdrawal_id.sudo()
            repayment = self.env['loan.manager.repayment'].browse(self.repayment_id.id).sudo()
            repayment.write({
                'withdrawal_id': withdrawal.id,
                'internal_payment': True
            })
            withdrawal.write({
                'loan_id': repayment.loan_id.id,
                'loan_repayment_id': repayment.id,
                'internal_used': True
            })
        return res