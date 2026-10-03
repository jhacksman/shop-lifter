import {ControlSession} from './controlSession';
function setup() {
  const pending = [];
  const socket = {connected: true, emit: jest.fn(), timeout: () => ({
    emit: (event, payload, callback) => pending.push({event, payload, callback})})};
  const session = new ControlSession(socket, () => [0.2, -0.2], jest.fn());
  return {session, socket, pending};
}
test('release while acquire is in flight cannot rearm', () => {
  const {session, pending} = setup();
  session.acquire(); session.release();
  pending[0].callback(null, {epoch: 'old'});
  expect(session.epoch).toBeNull(); expect(pending).toHaveLength(1);
});
test('bounded requests and fresh permit; rejected command revokes local authority', () => {
  const {session, pending} = setup();
  session.acquire(); pending[0].callback(null, {epoch: 'new'});
  session.pump(); session.pump(); expect(pending).toHaveLength(2);
  pending[1].callback(null, {permit: 'fresh'});
  expect(pending[2].payload).toEqual({epoch: 'new', permit: 'fresh', seq: 1,
    deadman: true, left: 0.2, right: -0.2});
  pending[2].callback(null, {accepted: false}); expect(session.epoch).toBeNull();
});
test('late heartbeat after release cannot enqueue drive', () => {
  const {session, pending} = setup();
  session.acquire(); pending[0].callback(null, {epoch: 'new'});
  session.release(); pending[1].callback(null, {permit: 'stale'});
  expect(pending).toHaveLength(2);
});
test('offline input never buffers acquisition', () => {
  const {session, socket, pending} = setup(); socket.connected = false;
  session.acquire(); expect(pending).toHaveLength(0);
});
test('ack timeout releases authority', () => {
  const {session, pending} = setup(); session.acquire();
  pending[0].callback(new Error('timeout')); expect(session.busy).toBe(false);
  expect(session.epoch).toBeNull();
});
