// One bounded request in flight. No Socket.IO offline command buffering.
export class ControlSession {
  constructor(socket, sample, update) {
    this.socket = socket;
    this.sample = sample;
    this.update = update;
    this.generation = 0;
    this.epoch = null;
    this.busy = false;
    this.sequence = 0;
  }
  request(event, payload, callback) {
    if (!this.socket.connected) { this.release(); return; }
    const generation = this.generation;
    this.socket.timeout(200).emit(event, payload, (error, response) => {
      if (generation !== this.generation) return;
      if (error) { this.release(); return; }
      callback(response);
    });
  }
  acquire() {
    if (this.busy || this.epoch || !this.socket.connected) return;
    this.busy = true;
    this.request('acquire', undefined, response => {
      this.busy = false;
      if (!response?.epoch) { this.update(response?.state); return; }
      this.epoch = response.epoch;
      this.sequence = 0;
      this.update(response.state);
      this.pump();
    });
  }
  pump() {
    if (!this.epoch || this.busy) return;
    this.busy = true;
    this.request('heartbeat', {epoch: this.epoch}, response => {
      if (!response?.permit) { this.release(); this.update(response?.state); return; }
      const [left, right] = this.sample();
      this.request('drive', {epoch: this.epoch, permit: response.permit,
        seq: ++this.sequence, left, right, deadman: true}, result => {
        this.busy = false;
        this.update(result?.state);
        if (!result?.accepted) this.release();
      });
    });
  }
  release() {
    this.generation += 1;
    this.epoch = null;
    this.busy = false;
    if (this.socket.connected) this.socket.emit('release');
    this.update({reason: 'released', output: [0, 0]});
  }
}
