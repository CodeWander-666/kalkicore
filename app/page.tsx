'use client';
import { useEffect, useRef } from 'react';

export default function Home() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      window.location.href = 'https://kalki-intelligence.in';
    }, 4000);

    const loadThree = async () => {
      const THREE = await import('three');
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.z = 15;

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      containerRef.current?.appendChild(renderer.domElement);

      // Cyan & Pink neon grid
      const gridHelper = new THREE.GridHelper(30, 30, 0x00ffff, 0xff00ff);
      gridHelper.material.transparent = true;
      gridHelper.material.opacity = 0.6;
      scene.add(gridHelper);

      const grid2 = new THREE.GridHelper(30, 30, 0xff00ff, 0x00ffff);
      grid2.rotation.x = Math.PI / 4;
      grid2.rotation.y = Math.PI / 4;
      grid2.material.transparent = true;
      grid2.material.opacity = 0.3;
      scene.add(grid2);

      // Particles
      const particlesGeometry = new THREE.BufferGeometry();
      const particlesCount = 2000;
      const posArray = new Float32Array(particlesCount * 3);
      for (let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 80;
      }
      particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
      const particlesMaterial = new THREE.PointsMaterial({
        size: 0.1,
        color: 0x00ffff,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending,
      });
      const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
      scene.add(particlesMesh);

      // Torus knot
      const geometry = new THREE.TorusKnotGeometry(2, 0.6, 150, 20);
      const material = new THREE.MeshStandardMaterial({
        color: 0xff00ff,
        emissive: 0x00ffff,
        emissiveIntensity: 0.4,
        metalness: 0.8,
        roughness: 0.2,
        wireframe: true,
      });
      const knot = new THREE.Mesh(geometry, material);
      knot.position.y = 0.5;
      scene.add(knot);

      // Lights
      const ambientLight = new THREE.AmbientLight(0x404060);
      scene.add(ambientLight);
      const light1 = new THREE.PointLight(0x00ffff, 1, 30);
      light1.position.set(5, 5, 5);
      scene.add(light1);
      const light2 = new THREE.PointLight(0xff00ff, 1, 30);
      light2.position.set(-5, -5, 5);
      scene.add(light2);

      let time = 0;
      const animate = () => {
        requestAnimationFrame(animate);
        time += 0.005;
        knot.rotation.x = time * 0.3;
        knot.rotation.y = time * 0.5;
        gridHelper.rotation.z = time * 0.02;
        grid2.rotation.x = Math.PI / 4 + time * 0.01;
        grid2.rotation.y = Math.PI / 4 + time * 0.02;
        particlesMesh.rotation.y = time * 0.005;
        renderer.render(scene, camera);
      };
      animate();

      const handleResize = () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      };
      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        renderer.domElement.remove();
        renderer.dispose();
      };
    };

    loadThree();
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <div ref={containerRef} style={{ position: 'fixed', inset: 0, zIndex: 0 }} />
      <div style={{
        position: 'fixed',
        inset: 0,
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        textAlign: 'center',
        pointerEvents: 'none',
        fontFamily: "'Courier New', monospace",
        textShadow: '0 0 20px rgba(0,255,255,0.3)',
      }}>
        <h1 style={{
          fontSize: 'clamp(2.5rem, 8vw, 5rem)',
          fontWeight: 700,
          background: 'linear-gradient(135deg, #00ffff, #ff00ff, #00ffff)',
          backgroundSize: '200% auto',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          animation: 'shimmer 3s ease infinite',
          letterSpacing: '0.2em',
        }}>
          KALKI TECHNOLOGIES
        </h1>
        <p style={{
          fontSize: 'clamp(1rem, 2.5vw, 1.8rem)',
          color: '#f0f0ff',
          marginTop: '1rem',
          letterSpacing: '0.1em',
          opacity: 0.9,
        }}>
          THE NEW ERA IS DEFINED ON<br />
          <strong style={{ color: '#00ffff', textShadow: '0 0 30px #00ffff' }}>kalki-intelligence.in</strong>
        </p>
        <div style={{
          marginTop: '2rem',
          fontSize: '0.9rem',
          color: 'rgba(255,255,255,0.4)',
          animation: 'pulse 1.5s ease-in-out infinite',
          letterSpacing: '0.15em',
        }}>
          ◈ REDIRECTING IN 4 SECONDS ◈
        </div>
      </div>
      <style>{`
        @keyframes shimmer {
          0% { background-position: 0% 50%; }
          100% { background-position: 200% 50%; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }
      `}</style>
    </>
  );
}
