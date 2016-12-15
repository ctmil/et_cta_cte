# -*- coding: utf-8 -*-
from openerp import models, api, fields, exceptions
from openerp.exceptions import ValidationError
from datetime import date

class account_invoice(models.Model):
	_inherit = "account.invoice"

	@api.one
	def _compute_amount_paid(self):
		self.amount_paid = self.amount_total - self.residual

	@api.one
	def _compute_text_payments(self):
		return_value = ''
		for payment in self.payment_ids:
			if self.type == 'out_invoice':
				return_value = str(payment.date) + ' - ' + payment.journal_id.name + ' - $' + str(payment.credit) + '\n'
			else:
				return_value = str(payment.date) + ' - ' + payment.journal_id.name + ' - $' + str(payment.debit) + '\n'
		self.text_payments = return_value

	amount_paid = fields.Float(string='Monto Pagado',compute=_compute_amount_paid)
	text_payments = fields.Text(string='Pagos',compute=_compute_text_payments)
