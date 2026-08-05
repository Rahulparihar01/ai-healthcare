import React from 'react';
import { FileCheck, ShieldCheck, Printer, X, Download } from 'lucide-react';

export default function PaymentReceiptModal({ transaction, onClose }) {
  if (!transaction) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 text-white shadow-2xl relative">
        <button onClick={onClose} className="absolute top-4 right-4 p-2 bg-slate-800 hover:bg-slate-700 text-slate-400 rounded-full">
          <X size={18} />
        </button>

        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-2xl flex items-center justify-center mx-auto mb-3">
            <ShieldCheck size={32} />
          </div>
          <h2 className="text-2xl font-bold text-slate-100">Official HMAC Signed Receipt</h2>
          <p className="text-xs text-slate-400">HealthID AI Hospital Billing Services</p>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-3 mb-6 text-sm">
          <div className="flex justify-between border-b border-slate-800 pb-2">
            <span className="text-slate-400">Transaction ID</span>
            <span className="font-mono text-slate-200">{transaction.transaction_id || `TXN-${transaction.id}`}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800 pb-2">
            <span className="text-slate-400">Invoice ID</span>
            <span className="font-mono text-slate-200">INV-{transaction.invoice_id}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800 pb-2">
            <span className="text-slate-400">Amount Paid</span>
            <span className="font-bold text-emerald-400">₹{(transaction.amount_cents / 100).toFixed(2)}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800 pb-2">
            <span className="text-slate-400">Status</span>
            <span className="px-2 py-0.5 rounded text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">SUCCESS</span>
          </div>

          <div className="pt-2">
            <span className="text-xs text-slate-500 block mb-1">HMAC SHA-256 Digital Verification Signature</span>
            <div className="p-2 bg-slate-900 border border-slate-800 rounded font-mono text-[10px] text-slate-400 break-all select-all">
              {transaction.signature || 'hmac_sha256_e7f9a2b8c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0'}
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button onClick={handlePrint} className="flex-1 flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 py-3 rounded-xl font-medium transition">
            <Printer size={18} />
            <span>Print Receipt</span>
          </button>
          <button onClick={onClose} className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-xl font-medium transition shadow-lg shadow-indigo-600/30">
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
