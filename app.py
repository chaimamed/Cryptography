from flask import Flask, render_template, request, url_for

app = Flask(__name__)

# human-friendly descriptions for the UI
ALGORITHM_INFO = {
    'caesar': {
        'name': 'Caesar Cipher',
        'description': 'Shifts each letter by a fixed number (the key). Only alphabetic characters are shifted; case is preserved.'
    },
    'substitution': {
        'name': 'Substitution Cipher',
        'description': 'A monoalphabetic substitution where each letter in the alphabet is replaced by a corresponding letter from the 26-character key.'
    },
    'vigenere': {
        'name': 'Vigenère Cipher',
        'description': 'A polyalphabetic substitution using a repeating keyword. The key and plaintext are aligned and letters are shifted by the key letter.'
    }
}

# Add more algorithms metadata
ALGORITHM_INFO.update({
    'atbash': {
        'name': 'Atbash Cipher',
        'description': 'A substitution cipher that maps a<->z, b<->y, etc. It is symmetric (same for encrypt/decrypt).'
    },
    'rot13': {
        'name': 'ROT13',
        'description': 'Caesar cipher with a fixed shift of 13. Useful for obfuscation, same operation for encrypt/decrypt.'
    },
    'xor': {
        'name': 'XOR Cipher (hex output)',
        'description': 'XOR each byte of the input with the key (repeating). Encryption outputs hex. For decryption, provide hex input.'
    }
})


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/solve', methods=['GET', 'POST'])
def solve_problem():
    algorithms = ALGORITHM_INFO
    # For GET requests render the solve form immediately (avoid referencing POST-only vars)
    if request.method != 'POST':
        return render_template('solve.html', algorithms=algorithms)

    # POST: process the submission
    if request.method == 'POST':
        algorithm = request.form.get('algorithm')
        mode = request.form.get('mode', 'encrypt')  # 'encrypt' or 'decrypt'
        plaintext = request.form.get('plaintext', '')
        key = request.form.get('key', '')

        if algorithm == 'caesar':
            try:
                shift = int(key)
            except Exception:
                solution = 'Invalid key for Caesar cipher. Use an integer.'
                return render_template('solution.html', algorithm=algorithm, plaintext=plaintext, key=key, solution=solution)
            if mode == 'encrypt':
                solution = caesar_encrypt(plaintext, shift)
            else:
                solution = caesar_decrypt(plaintext, shift)

        elif algorithm == 'substitution':
            if len(key) != 26 or not key.isalpha():
                solution = 'Invalid substitution key. Provide 26 alphabetic characters (a-z).'
            else:
                if mode == 'encrypt':
                    solution = substitution_encrypt(plaintext, key)
                else:
                    solution = substitution_decrypt(plaintext, key)

        elif algorithm == 'vigenere':
            if not key.isalpha():
                solution = 'Invalid Vigenère key. Use alphabetic characters only.'
            else:
                if mode == 'encrypt':
                    solution = vigenere_encrypt(plaintext, key)
                else:
                    solution = vigenere_decrypt(plaintext, key)
        elif algorithm == 'atbash':
            # Atbash is symmetric
            solution = atbash_cipher(plaintext)
        elif algorithm == 'rot13':
            solution = caesar_encrypt(plaintext, 13)
        elif algorithm == 'xor':
            # XOR: for encrypt -> produce hex, for decrypt -> expect hex
            if mode == 'encrypt':
                solution = xor_encrypt_to_hex(plaintext, key)
            else:
                solution = xor_decrypt_from_hex(plaintext, key)
        else:
            solution = 'Algorithm not supported.'

    # generate a short, helpful summary about the result for students
    result_summary = generate_result_summary(algorithm, mode, plaintext, key, solution)

    return render_template('solution.html', algorithm=algorithm, plaintext=plaintext, key=key, solution=solution, mode=mode, algorithms=algorithms, result_summary=result_summary)


# --- Algorithm implementations (educational, robust, preserve case & non-letters) ---

def caesar_shift_char(c, shift):
    if not c.isalpha():
        return c
    base = ord('A') if c.isupper() else ord('a')
    offset = (ord(c) - base + shift) % 26
    return chr(base + offset)


def caesar_encrypt(plaintext, shift):
    return ''.join(caesar_shift_char(c, shift) for c in plaintext)


def caesar_decrypt(ciphertext, shift):
    return ''.join(caesar_shift_char(c, -shift) for c in ciphertext)


def substitution_encrypt(plaintext, key):
    # key is 26 letters: maps 'a'..'z' to key[0]..key[25]
    key_lower = key.lower()
    mapping = {chr(ord('a') + i): key_lower[i] for i in range(26)}
    result = []
    for ch in plaintext:
        if ch.isalpha():
            mapped = mapping[ch.lower()]
            result.append(mapped.upper() if ch.isupper() else mapped)
        else:
            result.append(ch)
    return ''.join(result)


def substitution_decrypt(ciphertext, key):
    key_lower = key.lower()
    inv = {key_lower[i]: chr(ord('a') + i) for i in range(26)}
    result = []
    for ch in ciphertext:
        if ch.isalpha():
            orig = inv[ch.lower()]
            result.append(orig.upper() if ch.isupper() else orig)
        else:
            result.append(ch)
    return ''.join(result)


def vigenere_shift_char_encrypt(p, k):
    if not p.isalpha():
        return p
    base = ord('A') if p.isupper() else ord('a')
    kbase = ord('A') if k.isupper() else ord('a')
    shift = ord(k) - kbase
    return chr(base + (ord(p) - base + shift) % 26)


def vigenere_shift_char_decrypt(c, k):
    if not c.isalpha():
        return c
    base = ord('A') if c.isupper() else ord('a')
    kbase = ord('A') if k.isupper() else ord('a')
    shift = ord(k) - kbase
    return chr(base + (ord(c) - base - shift) % 26)


def vigenere_encrypt(plaintext, key):
    key_stream = [k for k in key if k.isalpha()]
    if not key_stream:
        return plaintext
    result = []
    j = 0
    for ch in plaintext:
        if ch.isalpha():
            k = key_stream[j % len(key_stream)]
            result.append(vigenere_shift_char_encrypt(ch, k))
            j += 1
        else:
            result.append(ch)
    return ''.join(result)


def vigenere_decrypt(ciphertext, key):
    key_stream = [k for k in key if k.isalpha()]
    if not key_stream:
        return ciphertext
    result = []
    j = 0
    for ch in ciphertext:
        if ch.isalpha():
            k = key_stream[j % len(key_stream)]
            result.append(vigenere_shift_char_decrypt(ch, k))
            j += 1
        else:
            result.append(ch)
    return ''.join(result)


# --- Additional algorithms ---
def atbash_cipher(text):
    result = []
    for ch in text:
        if ch.isalpha():
            if ch.isupper():
                result.append(chr(ord('Z') - (ord(ch) - ord('A'))))
            else:
                result.append(chr(ord('z') - (ord(ch) - ord('a'))))
        else:
            result.append(ch)
    return ''.join(result)


def xor_encrypt_to_hex(plaintext, key):
    if key == '':
        return 'Empty key for XOR'
    key_bytes = key.encode('utf-8')
    pt_bytes = plaintext.encode('utf-8')
    out = bytearray()
    for i, b in enumerate(pt_bytes):
        out.append(b ^ key_bytes[i % len(key_bytes)])
    return out.hex()


def xor_decrypt_from_hex(hextext, key):
    try:
        data = bytes.fromhex(hextext.strip())
    except Exception:
        return 'Invalid hex input for XOR decryption.'
    if key == '':
        return 'Empty key for XOR'
    key_bytes = key.encode('utf-8')
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key_bytes[i % len(key_bytes)])
    try:
        return out.decode('utf-8')
    except Exception:
        # return raw bytes hex if not UTF-8
        return out.hex()


def generate_result_summary(algorithm, mode, plaintext, key, solution):
    """Produce a short human-friendly summary explaining what happened and any notable characteristics."""
    info = ALGORITHM_INFO.get(algorithm, {})
    name = info.get('name', algorithm)
    # small heuristics
    length_in = len(plaintext or '')
    length_out = len(solution or '')
    parts = []
    parts.append(f"Used {name} ({mode}).")

    if algorithm in ('caesar', 'rot13'):
        parts.append("Alphabetic letters were shifted; case preserved.")
        if algorithm == 'caesar':
            try:
                parts.append(f"Shift/key: {int(key)}.")
            except Exception:
                pass
    elif algorithm == 'vigenere':
        parts.append("Polyalphabetic shifts using the provided keyword; non-letters left unchanged.")
    elif algorithm == 'substitution':
        parts.append("Letters were replaced using a monoalphabetic mapping from your 26-letter key.")
    elif algorithm == 'atbash':
        parts.append("Mapped letters to their reverse in the alphabet (a↔z).")
    elif algorithm == 'xor':
        if mode == 'encrypt':
            parts.append("Output is shown as hexadecimal bytes."
                         " To reverse, supply that hex and the same key in decrypt mode.")
        else:
            parts.append("Input hex was XOR-decrypted with the key; result attempted UTF-8 decode.")

    parts.append(f"Input length: {length_in} characters; Output length: {length_out} characters.")

    # short note about safety/education
    parts.append("This is an educational demonstration — do not use these simple ciphers for real security.")

    return ' '.join(parts)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
