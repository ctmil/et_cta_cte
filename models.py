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
				vals['tipo_doc'] = 'factura'
				vals['debe'] = invoice.amount_total
			else:
				vals['tipo_doc'] = 'nc'
				vals['haber'] = invoice.amount_total
			return_id = self.create(vals)
			if invoice.payment_ids:
				payments = {}
				for payment in invoice.payment_ids:
					voucher_lines = self.env['account.voucher.line'].search([('move_line_id','=',payment.id)])
					if voucher_lines:
						for voucher_line in voucher_lines:
							receipt_name = voucher_line.voucher_id.receipt_id.name or 'N/A'
							payment_amount = payments.get(receipt_name,0)
							payments[receipt_name] = payment_amount + payment.credit
					for key,value in payments.items():
						vals_payment = {
							'partner_id': payment.partner_id,
							'cliente_proveedor': 'cliente',
							'tipo_doc': 'pago',
							'ref': key,
							'fecha': payment.date,
							'haber': value			
							}
						return_id = self.create(vals_payment)
			

	fecha = fields.Date('Fecha')
	partner_id = fields.Many2one('res.partner',string='Cliente/Proveedor')
	cliente_proveedor = fields.Selection(selection=[('cliente','Cliente'),('proveedor','Proveedor')])
	tipo_doc = fields.Selection(selection=[('factura','FAC'),('nc','NC'),('pago','Pago')],string='Tipo Doc')
	ref = fields.Char('Numero')
	date = fields.Date(string='Fecha')
	debe = fields.Float('Debe')
	haber = fields.Float('Haber')
	
