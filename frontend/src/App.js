import React, { useState } from 'react';
import LoginForm from './components/LoginForm';
import ChatBox from './components/ChatBox';

function App() {
  const [user, setUser] = useState(null);

  return (
    <div className="App">
      {!user ? (
        <LoginForm onLogin={(userData) => setUser(userData)} />
      ) : (
        <ChatBox user={user} />
      )}
    </div>
  );
}

export default App;
