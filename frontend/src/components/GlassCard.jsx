import React from 'react';
import { motion } from 'framer-motion';

const GlassCard = ({ children, className = '', hover = true, neonColor = 'violet', onClick }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      onClick={onClick}
      className={`glass-card rounded-2xl p-6 ${hover ? 'glow-hover' : ''} ${className}`}
    >
      {children}
    </motion.div>
  );
};

export default GlassCard;