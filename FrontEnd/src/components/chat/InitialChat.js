import React from 'react';
import '../../styles/initial_chat.css';

function InitialChat() {
  return (
    <div className='initial_container'>
      <div className='intro_container'>
        <h3>Què ès Eulàlia?</h3>
        <p>Eulàlia és un assistent de xat dissenyat per oferir suport intern a l'equip de tècnics de l'Ajuntament de Barcelona.</p>
      </div>
      <div className='intro_container'>
        <h3>Com usar Eulàlia?</h3>
        <p>Per començar a parlar amb Eulàlia, simplement escriu la teva pregunta en el xat de sota.</p>
      </div>
    </div>
  );
}

export default InitialChat;