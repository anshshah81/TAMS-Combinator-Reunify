import React from 'react';

// Lightweight, reusable primitives styled with Tailwind and shared across
// intake forms, following shadcn/ui conventions without adding dependencies.

export function cx(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(' ');
}

export function Card({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cx('bg-white rounded-2xl border border-slate-200 shadow-sm p-6', className)}>{children}</div>;
}

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'danger';
};

export function Button({ variant = 'primary', className, ...props }: ButtonProps) {
  const styles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300',
    secondary: 'bg-white text-slate-800 border border-slate-300 hover:bg-slate-50 disabled:text-slate-400',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300',
  }[variant];
  return (
    <button
      {...props}
      className={cx('rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors disabled:cursor-not-allowed', styles, className)}
    />
  );
}

export function Field({ label, hint, required, children, htmlFor }: {
  label: string; hint?: string; required?: boolean; children: React.ReactNode; htmlFor?: string;
}) {
  return (
    <label htmlFor={htmlFor} className="block text-sm font-medium text-slate-700">
      <span>{label}{required && <span className="text-red-600" aria-hidden> *</span>}</span>
      <div className="mt-1">{children}</div>
      {hint && <span className="mt-1 block text-xs font-normal text-slate-500">{hint}</span>}
    </label>
  );
}

const control = 'w-full border border-slate-300 rounded-lg p-2.5 text-sm bg-white focus:border-blue-500';

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className, ...props }, ref) {
    return <input ref={ref} {...props} className={cx(control, className)} />;
  },
);

export const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  function Textarea({ className, ...props }, ref) {
    return <textarea ref={ref} {...props} className={cx(control, 'min-h-24', className)} />;
  },
);

export const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
  function Select({ className, children, ...props }, ref) {
    return <select ref={ref} {...props} className={cx(control, className)}>{children}</select>;
  },
);

export function Alert({ tone = 'info', children, role }: {
  tone?: 'info' | 'success' | 'error'; children: React.ReactNode; role?: string;
}) {
  const styles = {
    info: 'bg-blue-50 border-blue-200 text-blue-900',
    success: 'bg-emerald-50 border-emerald-200 text-emerald-900',
    error: 'bg-amber-50 border-amber-200 text-amber-900',
  }[tone];
  return <div role={role ?? (tone === 'error' ? 'alert' : 'status')} className={cx('border rounded-xl p-4 text-sm', styles)}>{children}</div>;
}

export function Badge({ children }: { children: React.ReactNode }) {
  return <span className="rounded-full bg-slate-100 text-slate-700 border border-slate-200 px-2.5 py-1 text-xs font-semibold capitalize">{children}</span>;
}
