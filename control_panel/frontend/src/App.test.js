import {render, screen} from '@testing-library/react';
import App from './App';
jest.mock('socket.io-client', () => ({io: () => ({connected: false,
  on: jest.fn(), connect: jest.fn(), disconnect: jest.fn()})}));
test('clearly identifies simulation and arm boundary', () => {
  render(<App/>);
  expect(screen.getByText(/no motors or arms connected/)).toBeInTheDocument();
  expect(screen.getByText(/Arm control remains separate/)).toBeInTheDocument();
});
