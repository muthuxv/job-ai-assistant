import React from 'react';

const NeonInput = ({ 
  label, 
  value, 
  onChange, 
  placeholder = '',
  type = 'text',
  required = false,
  className = ''
}) => {
  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label className="block text-sm font-medium mb-2 text-slate-300">
          {label}
          {required && <span className="text-neon-pink ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className="
          w-full px-4 py-3 rounded-xl
          bg-space-900/50 backdrop-blur-sm
          border border-white/10
          text-white placeholder-slate-500
          focus:outline-none focus:border-neon-violet
          focus:shadow-neon-violet
          transition-all duration-300
        "
      />
    </div>
  );
};

export default NeonInput;
