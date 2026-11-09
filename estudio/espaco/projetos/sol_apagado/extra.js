// Visão do chão depois que a luz do Sol acaba: o mar para de mexer e congela, e a geada cobre a areia.
// Usa o objeto "praia" do plano (céu de noite sem Lua). Registra "gelo" para a conferência.
export function montar({ THREE, scene, OBJ, tempo, registrar }) {
  const praia = OBJ.praia;
  const agua = praia.grupo.children[2];
  const ampBase = agua.material.uniforms.uAmp.value;
  const t = { calma0: tempo('C2'), calma1: tempo('C3.fim'), gelo0: tempo('C3'), gelo1: tempo('C4.2.fim'), fim: tempo('D1') };
  const suave = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
  const entre = (v, a, b) => (v - a) / Math.max(1e-6, b - a);

  // material do gelo: escuro sob as estrelas, com rachaduras e brilhos, sumindo na distância como o mar some no céu
  const matGelo = (claro, alcance) => new THREE.ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { uK: { value: 0 }, uClaro: { value: claro }, uAlc: { value: alcance } },
    vertexShader: 'varying vec3 vW; void main(){ vec4 w=modelMatrix*vec4(position,1.0); vW=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }',
    fragmentShader: `precision highp float; varying vec3 vW; uniform float uK,uClaro,uAlc;
      float h(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
      float n(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+1.0),f.x),f.y); }
      void main(){
        vec2 p=vW.xz; float d=distance(vW.xz,cameraPosition.xz);
        float m=0.6*n(p*0.35)+0.4*n(p*1.7);
        float rach=smoothstep(0.035,0.0,abs(n(p*0.22)-0.5))*0.8;          // rachaduras finas
        vec3 col=mix(vec3(0.10,0.14,0.20),vec3(0.24,0.31,0.40),m)*uClaro + vec3(0.30,0.40,0.55)*rach*0.35;
        float bril=step(0.997,h(floor(p*40.0)))*exp(-d/18.0)*0.8;             // cristais que pegam a luz das estrelas
        col+=vec3(0.75,0.85,1.0)*bril;
        float longe=exp(-d/uAlc);
        col=mix(vec3(0.012,0.02,0.05),col,longe);
        gl_FragColor=vec4(col,uK*0.96);
      }`,
  });
  const gMar = new THREE.PlaneGeometry(700, 560, 1, 1); gMar.rotateX(-Math.PI / 2); gMar.translate(0, 0.12, -279.5);
  const geloMar = new THREE.Mesh(gMar, matGelo(1.0, 70)); geloMar.renderOrder = 6;
  const gAreia = new THREE.PlaneGeometry(260, 20, 60, 20); gAreia.rotateX(-Math.PI / 2); gAreia.translate(0, 0, 9);
  { const p = gAreia.attributes.position; for (let i = 0; i < p.count; i++) p.setY(i, 0.1 * Math.min(p.getZ(i), 12) + 0.05); }
  const geada = new THREE.Mesh(gAreia, matGelo(1.25, 40)); geada.renderOrder = 6;
  scene.add(geloMar, geada);

  return {
    desenhar(tt) {
      const p = praia.grupo.position;
      const calma = suave(entre(tt, t.calma0, t.calma1));
      agua.material.uniforms.uAmp.value = ampBase * (1 - 0.92 * calma);
      const k = suave(entre(tt, t.gelo0, t.gelo1)) * (tt < t.fim ? 1 : 0);
      geloMar.position.copy(p); geada.position.copy(p);
      geloMar.material.uniforms.uK.value = k; geada.material.uniforms.uK.value = Math.min(1, k * 1.3) * 0.8;
      geloMar.visible = geada.visible = k > 0.002;
      if (k > 0.08) registrar('gelo', null, 0);
    },
  };
}
