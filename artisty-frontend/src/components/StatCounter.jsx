import React, { useEffect, useRef, useState } from 'react';

const clamp = (num, min, max) => Math.min(Math.max(num, min), max);

export default function StatCounter({ target = 0, durationMs = 2400, suffix = '', className = '' }) {
  const [value, setValue] = useState(0);
  const startedRef = useRef(false);

  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;

    const start = performance.now();
    const animate = (now) => {
      const elapsed = now - start;
      const progress = clamp(elapsed / durationMs, 0, 1);
      // Ease-out cubic for smoother finish
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(eased * target);
      setValue(current);
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  }, [target, durationMs]);

  return <span className={className}>{value}{suffix}</span>;
}
