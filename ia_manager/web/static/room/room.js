import * as THREE from './lib/three.module.min.js';

class RoomObject {
  constructor(id, mesh) {
    this.id = id;
    this.mesh = mesh;
    this.state = { on: true };
  }
  setState(state) {
    Object.assign(this.state, state);
    this.mesh.visible = this.state.on;
  }
}

class AIRoom {
  constructor() {
    this.objects = {};
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement);
    window.addEventListener('resize', () => this.onResize());
    this.camera.position.set(0, 2, 5);
    this.addLights();
    this.createObjects();
    this.animate();
    this.syncState();
    setInterval(() => this.syncState(), 5000);
  }
  addLights() {
    const amb = new THREE.AmbientLight(0xffffff, 0.5);
    const dir = new THREE.DirectionalLight(0xffffff, 0.5);
    dir.position.set(5,10,7);
    this.scene.add(amb, dir);
  }
  createObjects() {
    const floorGeo = new THREE.PlaneGeometry(10,10);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x555555 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI/2;
    this.scene.add(floor);

    // Bed
    const bedGeo = new THREE.BoxGeometry(2,0.5,1);
    const bedMat = new THREE.MeshStandardMaterial({ color: 0x8888ff });
    const bed = new THREE.Mesh(bedGeo, bedMat);
    bed.position.set(-2,0.25,0);
    this.scene.add(bed);
    this.objects['bed'] = new RoomObject('bed', bed);

    // Computer
    const monGeo = new THREE.BoxGeometry(1,0.6,0.1);
    const monMat = new THREE.MeshStandardMaterial({ color: 0x222222 });
    const monitor = new THREE.Mesh(monGeo, monMat);
    monitor.position.set(0,1, -1.5);
    this.scene.add(monitor);
    this.objects['computer'] = new RoomObject('computer', monitor);

    // Window
    const winGeo = new THREE.PlaneGeometry(2,1.5);
    const winMat = new THREE.MeshBasicMaterial({ color: 0x87ceeb });
    const windowMesh = new THREE.Mesh(winGeo, winMat);
    windowMesh.position.set(2,1.2,-2);
    this.scene.add(windowMesh);
    this.objects['window'] = new RoomObject('window', windowMesh);
  }
  onResize() {
    this.camera.aspect = window.innerWidth/window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }
  animate() {
    requestAnimationFrame(()=>this.animate());
    this.renderer.render(this.scene,this.camera);
  }
  async syncState() {
    const res = await fetch('/api/room/objects');
    const data = await res.json();
    data.forEach(obj=>{
      const local = this.objects[obj.id];
      if(local) local.setState(obj.state);
    });
  }
}

window.addEventListener('DOMContentLoaded', ()=> new AIRoom());
