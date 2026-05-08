import React from 'react';
import { motion } from 'framer-motion';

const NeonButton = ({ 
  children, 
  onClick, 
  variant = 'violet', 
  disabled = false,
  className = '',
  type = 'button'
}) => {
  const variantClass = {
    violet: 'btn-neon-violet',
    cyan: 'btn-neon-cyan',
    outline: 'border-2 border-purple-500 text-purple-400 hover:bg-purple-500/10',
  };

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.03 }}
      whileTap={{ scale: disabled ? 1 : 0.97 }}
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        px-6 py-3 rounded-xl font-semibold text-white
        ${variantClass[variant] || variantClass.violet}
        ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      {children}
    </motion.button>
  );
};

export default NeonButton;