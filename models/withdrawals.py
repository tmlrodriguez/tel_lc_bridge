from odoo import models, fields

class WithdrawalBridge(models.Model):
    _inherit = 'contributions.manager.withdrawal'

    loan_id = fields.Many2one('loan.manager.loan', string='Préstamo Asociado', readonly=True)
    loan_repayment_id = fields.Many2one('loan.manager.repayment', string='Cuota Asociada', readonly=True)