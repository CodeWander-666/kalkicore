'use client';
import { useState, useEffect, useRef } from 'react';

interface OptimizedVideoProps {
  src: string;
  poster?: string;
  className?: string;
  autoPlay?: boolean;
  loop?: boolean;
  muted?: boolean;
  playsInline?: boolean;
  lazy?: boolean;
  children?: React.ReactNode;
}

export function OptimizedVideo({
  src,
  poster,
  className = '',
  autoPlay = false,
  loop = false,
  muted = true,
  playsInline = true,
  lazy = true,
  children,
}: OptimizedVideoProps) {
  const [isVisible, setIsVisible] = useState(!lazy);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (!lazy) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true);
            observer.disconnect();
          }
        });
      },
      { rootMargin: '100px' }
    );
    if (videoRef.current) observer.observe(videoRef.current);
    return () => observer.disconnect();
  }, [lazy]);

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {isVisible ? (
        <video
          ref={videoRef}
          src={src}
          poster={poster}
          autoPlay={autoPlay}
          loop={loop}
          muted={muted}
          playsInline={playsInline}
          className="w-full h-full object-cover"
          preload="none"
        >
          {children}
        </video>
      ) : (
        <div className="w-full h-full bg-black/20 animate-pulse" />
      )}
    </div>
  );
}
