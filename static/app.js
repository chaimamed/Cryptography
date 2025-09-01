// Small UI helpers for the CryptoLearn solve page
(function(){
  const algoSelect = document.getElementById('algorithm');
  const algoName = document.getElementById('algoName');
  const algoDesc = document.getElementById('algoDesc');
  const keyHint = document.getElementById('key-hint');
  const clearBtn = document.getElementById('clearBtn');

  const ALGOS = {
    caesar: {
      name: 'Caesar Cipher',
      desc: 'Shift letters by an integer key. Use a small integer like 3. Non-letters are preserved and case is kept.',
      hint: 'Integer (e.g. 3 or -5)'
    },
    substitution: {
      name: 'Substitution Cipher',
      desc: 'Monoalphabetic substitution. Provide a 26-letter key mapping a->key[0], b->key[1], ... (letters only).',
      hint: '26 letters (a-z)'
    },
    vigenere: {
      name: 'Vigenère Cipher',
      desc: 'Use an alphabetic keyword that repeats over the plaintext. Only letters in the key are used.',
      hint: 'Alphabetic keyword (e.g. SECRET)'
    }
    ,atbash: {
      name: 'Atbash Cipher',
      desc: 'Substitute letters with their reverse in the alphabet (a<->z). Same operation for encrypt/decrypt.',
      hint: 'No key required'
    },
    rot13: {
      name: 'ROT13',
      desc: 'Fixed Caesar shift of 13. Same operation encrypt/decrypt. Good for quick obfuscation.',
      hint: 'No key required'
    },
    xor: {
      name: 'XOR Cipher',
      desc: 'XOR each byte with the repeating key. Encrypt outputs hex; for decrypt provide hex input.',
      hint: 'Key string (any text). For decrypt supply hex input in the text box.'
    }
  };

  function updateInfo(){
    const key = algoSelect.value;
    const meta = ALGOS[key] || {name:'',desc:'',hint:''};
    if(algoName) algoName.textContent = meta.name;
    if(algoDesc) algoDesc.textContent = meta.desc;
    if(keyHint) keyHint.textContent = meta.hint;
  }

  if(algoSelect) algoSelect.addEventListener('change', updateInfo);
  if(clearBtn){
    clearBtn.addEventListener('click', ()=>{
      document.getElementById('plaintext').value = '';
      document.getElementById('key').value = '';
    });
  }

  // init
  updateInfo();
})();
