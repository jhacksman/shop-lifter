// Derived from Enzo Marrama and jhacksman's shoppy React/Chakra tank controls.
import React, {useEffect, useRef, useState} from 'react';
import {ChakraProvider, Box, VStack, HStack, Text, Button, Select,
  Slider, SliderTrack, SliderFilledTrack, SliderThumb, Alert, AlertIcon} from '@chakra-ui/react';
import {io} from 'socket.io-client';
import {ControlSession} from './controlSession';

export default function App() {
  const [connected, setConnected] = useState(false);
  const [state, setState] = useState({reason: 'disconnected', output: [0, 0]});
  const [power, setPower] = useState([0, 0]);
  const [mode, setMode] = useState('touch');
  const inputs = useRef([0, 0]);
  const transport = useRef(null);
  const session = useRef(null);
  const selectedMode = useRef(mode);
  const stop = () => {
    inputs.current = [0, 0]; setPower([0, 0]);
    session.current?.release();
  };

  useEffect(() => {
    // No implicit reconnect/re-arm. Operator must reconnect, then hold again.
    const socket = io(process.env.REACT_APP_CONTROL_URL || 'http://127.0.0.1:5050',
      {autoConnect: false, reconnection: false});
    transport.current = socket;
    const control = new ControlSession(socket, () => inputs.current,
      value => value && setState(previous => ({...previous, ...value})));
    session.current = control;
    const clear = () => {
      inputs.current = [0, 0]; setPower([0, 0]); control.release();
    };
    const disconnected = () => { clear(); setConnected(false); };
    socket.on('connect', () => { clear(); setConnected(true); });
    socket.on('disconnect', disconnected);
    socket.on('connect_error', disconnected);
    socket.on('state', value => { clear(); setState(value); });
    const keys = new Set();
    let space = false;
    let gamepadHeld = false;
    let gamepadReady = false;
    const keydown = event => {
      if (selectedMode.current !== 'keyboard' || event.repeat) return;
      if (![' ', 'f', 'v', 'j', 'n'].includes(event.key.toLowerCase())) return;
      event.preventDefault(); keys.add(event.key.toLowerCase());
      if (event.key === ' ' && !space) { space = true; control.acquire(); }
    };
    const keyup = event => {
      keys.delete(event.key.toLowerCase());
      if (event.key === ' ') { space = false; clear(); }
    };
    const blur = () => { keys.clear(); space = false; gamepadHeld = false; gamepadReady = false; clear(); };
    const visibility = () => { if (document.hidden) blur(); };
    const timer = setInterval(() => {
      if (document.hidden || !document.hasFocus()) { blur(); return; }
      if (selectedMode.current === 'keyboard') {
        inputs.current = [(Number(keys.has('f')) - Number(keys.has('v'))) * 0.5,
          (Number(keys.has('j')) - Number(keys.has('n'))) * 0.5];
        setPower([...inputs.current]);
      }
      if (selectedMode.current === 'gamepad') {
        const pad = Array.from(navigator.getGamepads?.() || []).find(Boolean);
        const held = Boolean(pad?.buttons[4]?.pressed);
        if (!held) gamepadReady = true;
        if (!held && gamepadHeld) clear();
        if (held && !gamepadHeld && gamepadReady) { gamepadReady = false; control.acquire(); }
        gamepadHeld = held;
        inputs.current = pad ? [pad.axes[1], pad.axes[3]].map(value =>
          Number.isFinite(value) && Math.abs(value) >= 0.1 ? -value : 0) : [0, 0];
        setPower([...inputs.current]);
      } else { gamepadHeld = false; gamepadReady = false; }
      control.pump();
    }, 80);
    window.addEventListener('keydown', keydown);
    window.addEventListener('keyup', keyup);
    window.addEventListener('blur', blur);
    window.addEventListener('gamepaddisconnected', blur);
    document.addEventListener('visibilitychange', visibility);
    socket.connect();
    return () => {
      clearInterval(timer); clear(); socket.disconnect();
      window.removeEventListener('keydown', keydown);
      window.removeEventListener('keyup', keyup);
      window.removeEventListener('blur', blur);
      window.removeEventListener('gamepaddisconnected', blur);
      document.removeEventListener('visibilitychange', visibility);
    };
  }, []);

  return <ChakraProvider><Box maxW="800px" mx="auto" p={8}><VStack spacing={6} align="stretch">
    <Text as="h1" fontSize="3xl">shop-lifter control</Text>
    <Alert status="info"><AlertIcon/>Simulation only — no motors or arms connected.</Alert>
    <Text>Connection: {connected ? 'connected' : 'disconnected'} · {state.reason}</Text>
    <Text>Applied simulated output: {(state.output || [0, 0]).map(v => v.toFixed(2)).join(' / ')}</Text>
    <Select aria-label="Control method" value={mode} onChange={event => {
      stop(); selectedMode.current = event.target.value; setMode(event.target.value);
    }}><option value="touch">Touch / mouse</option><option value="keyboard">Keyboard</option>
      <option value="gamepad">Gamepad</option></Select>
    {mode === 'touch' && <>
      {['Left', 'Right'].map((name, index) => <Box key={name}>
        <Text>{name} request: {power[index].toFixed(2)}</Text>
        <Slider aria-label={`${name} wheel`} min={-1} max={1} step={0.05}
          value={power[index]} isDisabled={!connected || state.estopped}
          onChange={value => {
            inputs.current = inputs.current.map((v, i) => i === index ? value : v);
            setPower([...inputs.current]);
          }}><SliderTrack><SliderFilledTrack/></SliderTrack><SliderThumb/></Slider>
      </Box>)}
      <Button style={{touchAction: 'none'}} isDisabled={!connected || state.estopped}
        onPointerDown={event => {event.currentTarget.setPointerCapture(event.pointerId); session.current.acquire();}}
        onPointerUp={stop} onPointerCancel={stop} onLostPointerCapture={stop}>Hold to drive</Button>
    </>}
    {mode === 'keyboard' && <Text>Hold Space to enable. Hold F/V for left forward/reverse and J/N for right. Release Space to stop.</Text>}
    {mode === 'gamepad' && <Text>Hold left shoulder (button 4); use the two vertical sticks. Release shoulder to stop.</Text>}
    <HStack flexWrap="wrap">
      <Button colorScheme="red" onClick={() => {stop(); if (transport.current.connected) transport.current.emit('estop');}}>Latch software stop</Button>
      <Button onClick={() => {stop(); if (transport.current.connected) transport.current.emit('reset');}}>Reset latch (stays stopped)</Button>
      <Button isDisabled={connected} onClick={() => {stop(); transport.current.connect();}}>Reconnect</Button>
    </HStack>
    <Text fontSize="sm">This software stop is not an electrical emergency stop. Simulation does not prove physical safety. Arm control remains separate.</Text>
  </VStack></Box></ChakraProvider>;
}
