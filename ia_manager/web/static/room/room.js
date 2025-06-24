class RoomObject {
  constructor(id, x, y, w, h, color) {
    this.id = id;
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
    this.color = color;
    this.state = { on: true };
  }
  setState(state) {
    Object.assign(this.state, state);
    if (state.color) this.color = state.color;
  }
  draw(ctx) {
    if (!this.state.on) return;
    ctx.fillStyle = this.color;
    ctx.fillRect(this.x, this.y, this.w, this.h);
  }
}

class AIRoom {
  constructor() {
    this.objects = {};
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    document.body.appendChild(this.canvas);
    window.addEventListener('resize', () => this.onResize());
    this.createObjects();
    this.onResize();
    this.loop();
    this.syncState();
    setInterval(() => this.syncState(), 5000);
  }
  createObjects() {
    this.objects['bed'] = new RoomObject('bed', 50, 150, 80, 40, '#8888ff');
    this.objects['computer'] = new RoomObject('computer', 200, 120, 40, 30, '#222222');
    this.objects['window'] = new RoomObject('window', 300, 60, 70, 50, '#87ceeb');
  }
  onResize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }
  loop() {
    requestAnimationFrame(() => this.loop());
    this.ctx.fillStyle = '#000';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    for (const obj of Object.values(this.objects)) {
      obj.draw(this.ctx);
    }
  }
  async syncState() {
    try {
      const res = await fetch('/api/room/objects');
      const data = await res.json();
      data.forEach(obj => {
        const local = this.objects[obj.id];
        if (local) local.setState(obj.state);
      });
    } catch (err) {
      console.error(err);
    }
  }
}

window.addEventListener('DOMContentLoaded', () => new AIRoom());
