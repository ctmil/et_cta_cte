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
				return_value = return_value + str(payment.date) + ' - ' + payment.journal_id.name + ' - $' + str(payment.credit) + '\n'
			else:
				return_value = return_value + str(payment.date) + ' - ' + payment.journal_id.name + ' - $' + str(payment.debit) + '\n'
		self.text_payments = return_value

	amount_paid = fields.Float(string='Monto Pagado',compute=_compute_amount_paid)
	text_payments = fields.Text(string='Pagos',compute=_compute_text_payments)


class partner_cta_cte(models.Model):
	_name = 'partner.cta.cte'
	_description = 'Partner Cta Cte'

	@api.model
	def _compute_partner_cta_cte(self):
                self.search([]).unlink()
                invoices = self.env['account.invoice'].search([('state','in',['open','paid']),('type','in',['out_refund','out_invoice'])])
		for invoice in invoices:
			vals = {
				'partner_id': invoice.partner_id.id,
				'cliente_proveedor': 'cliente',
				'ref': invoice.number,
				'fecha': invoice.date_invoice,
				}
			if invoice.type == 'out_invoice':
				vals['factura_nc'] = 'factura'
				vals['debe'] = invoice.amount_total
			else:
				vals['factura_nc'] = 'nc'
				vals['haber'] = invoice.amount_total
			return_id = self.create(vals)
			

	fecha = fields.Date('Fecha')
	partner_id = fields.Many2one('res.partner',string='Cliente/Proveedor')
	cliente_proveedor = fields.Selection(selection=[('cliente','Cliente'),('proveedor','Proveedor')])
	tipo_doc = fields.Selection(selection=[('factura','FAC'),('nc','NC'),('pago','Pago')],string='Tipo Doc')
	ref = fields.Char('Numero')
	date = fields.Date(string='Fecha')
	debe = fields.Float('Debe')
	haber = fields.Float('Haber')
	
