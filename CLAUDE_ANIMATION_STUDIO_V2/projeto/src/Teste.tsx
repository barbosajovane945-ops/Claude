import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

// Vídeo de teste: 5 s, vertical, fundo colorido e o texto "OLÁ" entrando com mola.
export const Teste: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const scale = spring({frame, fps, config: {damping: 12, stiffness: 120}});
	const opacity = interpolate(frame, [0, 12], [0, 1], {extrapolateRight: 'clamp'});

	return (
		<AbsoluteFill style={{background: 'linear-gradient(160deg, #ff7a59 0%, #7b5cff 100%)', justifyContent: 'center', alignItems: 'center'}}>
			<div
				style={{
					fontFamily: 'Arial, Helvetica, sans-serif',
					fontWeight: 900,
					fontSize: 260,
					color: '#ffffff',
					opacity,
					transform: `scale(${scale})`,
					textShadow: '0 12px 40px rgba(0,0,0,0.25)',
				}}
			>
				OLÁ
			</div>
		</AbsoluteFill>
	);
};
