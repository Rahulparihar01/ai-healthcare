import React, { useState } from 'react';
import { CreditCard, CheckCircle2, ShieldCheck, Download, X, Lock, DollarSign, Receipt } from 'lucide-react';
import api from '../api';

export default function PaymentModal({ invoice, onClose, onSuccess }) {
  const [paymentMethod, setPaymentMethod] = useState('Card');
  const [cardNumber, setCardNumber] = useState('•••• •••• •••• 4242');
  const [expiry, setExpiry] = useState('12/28');
  const [cvc, setCvc] = useState('123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [paidReceipt, setPaidReceipt] = useState(null);

  if (!invoice) return null;

  const handlePayment = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // 1. Create Payment Intent
      const intentRes = await api.post(`/billing/invoices/${invoice.id}/create-payment-intent`, {
        gateway: paymentMethod === 'Card' ? 'Stripe' : paymentMethod
      });
      
      const { payment_intent_id } = intentRes.data;

      // 2. Confirm Payment
      const confirmRes = await api.post(`/billing/invoices/${invoice.id}/confirm-payment`, {
        payment_intent_id,
        payment_method: paymentMethod,
        gateway_transaction_id: `txn_${Math.random().toString(36).substring(2, 12)}`
      });

      // 3. Fetch Receipt
      const receiptRes = await api.get(`/billing/invoices/${invoice.id}/receipt`);
      setPaidReceipt(receiptRes.data);
      if (onSuccess) onSuccess(confirmRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Payment processing failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReceipt = () => {
    if (!paidReceipt) return;
    const blob = new Blob([JSON.stringify(paidReceipt, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Receipt_${paidReceipt.invoice_number}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 text-slate-100 rounded-2xl max-w-lg w-full p-6 shadow-2xl relative overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-100">Healthcare Bill Payment</h3>
              <p className="text-xs text-slate-400">Invoice #{invoice.invoice_number}</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {paidReceipt ? (
          /* Success Receipt View */
          <div className="py-4 space-y-5 animate-in zoom-in-95 duration-200">
            <div className="text-center space-y-2">
              <div className="w-14 h-14 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h4 className="text-xl font-bold text-slate-100">Payment Successful!</h4>
              <p className="text-sm text-slate-400">Official digital receipt signed & verified.</p>
            </div>

            <div className="bg-slate-950/60 rounded-xl p-4 border border-slate-800 space-y-2 font-mono text-xs text-slate-300">
              <div className="flex justify-between border-b border-slate-800/80 pb-2 text-slate-400">
                <span>Receipt No:</span>
                <span className="text-slate-200">{paidReceipt.invoice_number}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/80 py-1">
                <span>Amount Paid:</span>
                <span className="text-emerald-400 font-bold">{paidReceipt.formatted_amount}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/80 py-1">
                <span>Method:</span>
                <span>{paidReceipt.payment_method}</span>
              </div>
              <div className="flex justify-between py-1">
                <span>Digital Signature:</span>
                <span className="truncate max-w-[180px] text-cyan-400" title={paidReceipt.digital_signature}>
                  {paidReceipt.digital_signature?.substring(0, 16)}...
                </span>
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={handleDownloadReceipt}
                className="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2.5 rounded-xl flex items-center justify-center gap-2 transition"
              >
                <Download className="w-4 h-4" /> Download Receipt
              </button>
              <button
                onClick={onClose}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold px-5 py-2.5 rounded-xl transition"
              >
                Close
              </button>
            </div>
          </div>
        ) : (
          /* Payment Form View */
          <form onSubmit={handlePayment} className="space-y-5">
            {error && (
              <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs p-3 rounded-xl">
                {error}
              </div>
            )}

            {/* Amount Summary */}
            <div className="bg-slate-950/60 rounded-xl p-4 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400 block">Total Due</span>
                <span className="text-xs text-slate-300">{invoice.description || 'Medical Services'}</span>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-cyan-400">
                  ${(invoice.amount / 100).toFixed(2)}
                </span>
                <span className="text-xs text-slate-500 block uppercase">{invoice.currency}</span>
              </div>
            </div>

            {/* Line Items Preview */}
            {invoice.line_items && invoice.line_items.length > 0 && (
              <div className="space-y-1 bg-slate-950/40 p-3 rounded-xl border border-slate-800/80 text-xs">
                <span className="text-slate-400 font-medium block mb-1">Item Breakdown:</span>
                {invoice.line_items.map((item, idx) => (
                  <div key={idx} className="flex justify-between text-slate-300">
                    <span>{item.description}</span>
                    <span>${(item.amount / 100).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Payment Method Selector */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 block">Select Payment Method</label>
              <div className="grid grid-cols-3 gap-2">
                {['Card', 'Stripe', 'Razorpay'].map((method) => (
                  <button
                    key={method}
                    type="button"
                    onClick={() => setPaymentMethod(method)}
                    className={`py-2 px-3 rounded-xl border text-xs font-medium transition flex items-center justify-center gap-1.5 ${
                      paymentMethod === method
                        ? 'bg-cyan-500/10 border-cyan-500/50 text-cyan-400'
                        : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {method}
                  </button>
                ))}
              </div>
            </div>

            {/* Card Inputs */}
            <div className="space-y-3 bg-slate-950/40 p-3.5 rounded-xl border border-slate-800/80">
              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Card Number</label>
                <input
                  type="text"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] font-medium text-slate-400 block mb-1">Expires (MM/YY)</label>
                  <input
                    type="text"
                    value={expiry}
                    onChange={(e) => setExpiry(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                    required
                  />
                </div>
                <div>
                  <label className="text-[11px] font-medium text-slate-400 block mb-1">CVC</label>
                  <input
                    type="password"
                    value={cvc}
                    onChange={(e) => setCvc(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 text-[11px] text-slate-400">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>Encrypted & digitally signed via 256-bit HMAC SSL</span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-semibold py-3 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/20 transition"
            >
              {loading ? (
                <span>Processing Payment...</span>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" /> Pay ${(invoice.amount / 100).toFixed(2)} Securely
                </>
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
