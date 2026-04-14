import { useState } from 'react';
import { X, LogIn, UserPlus, Eye, EyeOff } from 'lucide-react';

function formatApiError(detail) {
  if (detail == null) return 'Something went wrong. Please try again.';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map(e => e?.msg || JSON.stringify(e)).join(' ');
  if (detail?.msg) return detail.msg;
  return String(detail);
}

const AuthModal = ({ isOpen, onClose, onAuth, apiUrl }) => {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const url = mode === 'login' ? `${apiUrl}/auth/login` : `${apiUrl}/auth/register`;
      const body = mode === 'login'
        ? { email, password }
        : { email, password, name };
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(formatApiError(data.detail));
        return;
      }
      onAuth(data.user, data.token);
      onClose();
      setEmail('');
      setPassword('');
      setName('');
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4" data-testid="auth-modal">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-sm bg-[#111111] border border-white/[0.1] p-6 z-10">
        <button onClick={onClose} className="absolute top-4 right-4 text-[#737373] hover:text-[#FAFAFA] transition-colors" data-testid="auth-modal-close">
          <X size={18} />
        </button>

        <h2 className="font-heading text-xl text-[#FAFAFA] mb-1">
          {mode === 'login' ? 'Iniciar Sesion' : 'Crear Cuenta'}
        </h2>
        <p className="text-xs text-[#737373] mb-5">
          {mode === 'login' ? 'Accede a tus favoritos personales' : 'Guarda tus cacerias favoritas'}
        </p>

        <div className="flex gap-1 mb-5 p-0.5 bg-white/[0.04] border border-white/[0.08]">
          <button
            onClick={() => { setMode('login'); setError(''); }}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-mono transition-colors ${mode === 'login' ? 'bg-[#C5A059] text-black' : 'text-[#A3A3A3] hover:text-[#FAFAFA]'}`}
            data-testid="auth-tab-login"
          >
            <LogIn size={13} /> Login
          </button>
          <button
            onClick={() => { setMode('register'); setError(''); }}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-mono transition-colors ${mode === 'register' ? 'bg-[#C5A059] text-black' : 'text-[#A3A3A3] hover:text-[#FAFAFA]'}`}
            data-testid="auth-tab-register"
          >
            <UserPlus size={13} /> Registro
          </button>
        </div>

        {error && (
          <div className="mb-4 p-2.5 text-xs text-red-400 bg-red-500/10 border border-red-500/20" data-testid="auth-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          {mode === 'register' && (
            <div>
              <label className="block text-[10px] font-mono text-[#737373] uppercase tracking-wider mb-1">Nombre</label>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                className="w-full px-3 py-2 bg-white/[0.04] border border-white/[0.1] text-sm text-[#FAFAFA] placeholder-[#737373] focus:border-[#C5A059]/50 focus:outline-none transition-colors"
                placeholder="Tu nombre"
                required
                data-testid="auth-name-input"
              />
            </div>
          )}
          <div>
            <label className="block text-[10px] font-mono text-[#737373] uppercase tracking-wider mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-white/[0.04] border border-white/[0.1] text-sm text-[#FAFAFA] placeholder-[#737373] focus:border-[#C5A059]/50 focus:outline-none transition-colors"
              placeholder="tu@email.com"
              required
              data-testid="auth-email-input"
            />
          </div>
          <div>
            <label className="block text-[10px] font-mono text-[#737373] uppercase tracking-wider mb-1">Password</label>
            <div className="relative">
              <input
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full px-3 py-2 pr-10 bg-white/[0.04] border border-white/[0.1] text-sm text-[#FAFAFA] placeholder-[#737373] focus:border-[#C5A059]/50 focus:outline-none transition-colors"
                placeholder="Min 6 caracteres"
                required
                minLength={6}
                data-testid="auth-password-input"
              />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#737373] hover:text-[#FAFAFA]">
                {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-[#C5A059] text-black text-sm font-semibold hover:bg-[#D4AF37] transition-colors disabled:opacity-50"
            data-testid="auth-submit-btn"
          >
            {loading ? 'Procesando...' : mode === 'login' ? 'Iniciar Sesion' : 'Crear Cuenta'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AuthModal;
