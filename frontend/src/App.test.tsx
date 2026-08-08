import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

jest.mock('./pages/StoryList', () => () => <h1>My Stories</h1>);

test('renders the novel writer home screen', () => {
  render(<App />);
  expect(screen.getByText('AI Novel Writer')).toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'My Stories' })).toBeInTheDocument();
});
