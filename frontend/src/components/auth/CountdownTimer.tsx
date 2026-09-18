"use client";

import { useEffect, useRef, useState } from "react";

interface CountdownTimerProps {
  seconds: number; // مقدار شروع (مثلا ۱۲۰)
  onExpire?: () => void;
  resetKey?: number; // با تغییر این مقدار، تایمر از نو شروع می‌شود
}

export function CountdownTimer({ seconds, onExpire, resetKey }: CountdownTimerProps) {
  const [remaining, setRemaining] = useState(seconds);
  const onExpireRef = useRef(onExpire);
  onExpireRef.current = onExpire;

  useEffect(() => {
    setRemaining(seconds);
  }, [seconds, resetKey]);

  useEffect(() => {
    if (remaining <= 0) {
      onExpireRef.current?.();
      return;
    }
    const id = setTimeout(() => setRemaining((r) => r - 1), 1000);
    return () => clearTimeout(id);
  }, [remaining]);

  const mm = String(Math.floor(remaining / 60)).padStart(2, "0");
  const ss = String(remaining % 60).padStart(2, "0");

  return (
    <span dir="ltr" className="tabular-nums text-text-secondary">
      {mm}:{ss}
    </span>
  );
}
