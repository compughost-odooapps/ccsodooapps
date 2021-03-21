from datetime import datetime
from odoo import api, fields, models
from odoo.tests import Form


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    is_validate_picking = fields.Boolean('Validate Delivery Order')

    is_create_invoice = fields.Boolean('Create Invoice')
    is_validate_invoice = fields.Boolean('Validate Invoice')
    is_register_payment = fields.Boolean('Register Payment')

    @api.onchange('is_create_invoice', 'is_validate_invoice')
    def _onchange_mark_recompute_taxes_analytic(self):
        for record in self:
            if not record.is_validate_invoice:
                record.is_register_payment = False

            elif not record.is_create_invoice:
                record.is_validate_invoice = False
                record.is_register_payment = False


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_auto_confirm(self):
        for order in self:
            order.action_confirm()
            warehouse_id = order.warehouse_id

            if warehouse_id.is_validate_picking:
                for picking in order.picking_ids.filtered(lambda p:  p.state not in ('done', 'cancel')):
                    picking.action_assign()
                    res = picking.button_validate()
                    wiz = Form(self.env['stock.immediate.transfer'].with_context(res['context'])).save()
                    wiz.process()

            if warehouse_id.is_create_invoice:
                invoice_wiz = self.env['sale.advance.payment.inv'].with_context(
                    active_ids=order.ids, open_invoices=False).create({
                    'advance_payment_method': 'delivered'
                    })
                invoice = invoice_wiz.create_invoices()

                if warehouse_id.is_validate_invoice:
                    for invoice in order.invoice_ids.filtered(lambda i:  i.state not in ('done', 'cancel')):
                        invoice.action_post()

                        if warehouse_id.is_register_payment:
                            pmt_wizard = self.env['account.payment.register'].with_context(
                                active_model='account.move', active_ids=invoice.ids).create({
                                'payment_date': datetime.today().date(),
                            })
                            pmt_wizard._compute_amount()
                            pmt_wizard._compute_journal_id()
                            pmt_wizard._compute_communication()
                            pmt_wizard._create_payments()

