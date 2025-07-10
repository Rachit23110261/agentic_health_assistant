import React, { useState } from 'react';
import axios from 'axios';

function LoginForm({ onLogin }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('patient');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!name || !email || !role) return alert('Please fill in all fields.');

    try {
      const res = await axios.post('https://agentic-health-assistant-fupm.onrender.com/api/login', null, {
        params: { name, email, role }
      });
      onLogin(res.data); 
    } catch (err) {
      console.error('Login failed', err);
      alert('Login failed.');
    }
  };

  return (
    <form className="login-box" onSubmit={handleLogin}>
      <h2>Sign In</h2>
      <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
      <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <select value={role} onChange={(e) => setRole(e.target.value)}>
        <option value="patient">Patient</option>
        <option value="doctor">Doctor</option>
      </select>
      <button type="submit">Login</button>
    </form>
  );
}

export default LoginForm;
