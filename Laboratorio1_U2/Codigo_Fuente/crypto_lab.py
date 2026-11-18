#!/usr/bin/env python3
"""Demostraciones criptográficas educativas. No usar como sistema productivo."""
import argparse, os, hashlib, base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

def load_private(path):
    return serialization.load_pem_private_key(Path(path).read_bytes(), password=None)

def load_public(path):
    return serialization.load_pem_public_key(Path(path).read_bytes())

def main():
    p = argparse.ArgumentParser(description="Laboratorio de criptografía")
    sub = p.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("hash"); h.add_argument("file")
    e = sub.add_parser("encrypt"); e.add_argument("file"); e.add_argument("--key", default="aes.key")
    d = sub.add_parser("decrypt"); d.add_argument("file"); d.add_argument("--key", default="aes.key")
    k = sub.add_parser("rsa-keys"); k.add_argument("--private", default="rsa_private.pem"); k.add_argument("--public", default="rsa_public.pem")
    w = sub.add_parser("rsa-wrap"); w.add_argument("text"); w.add_argument("--public", default="rsa_public.pem")
    u = sub.add_parser("rsa-unlock"); u.add_argument("file", nargs="?", default="rsa_message.bin"); u.add_argument("--private", default="rsa_private.pem")
    s = sub.add_parser("sign"); s.add_argument("file"); s.add_argument("--private", default="rsa_private.pem")
    v = sub.add_parser("verify"); v.add_argument("file"); v.add_argument("signature"); v.add_argument("--public", default="rsa_public.pem")
    ph = sub.add_parser("password-hash")
    pc = sub.add_parser("password-check"); pc.add_argument("stored_hash")
    sub.add_parser("ecdh-demo")

    a = p.parse_args()
    if a.cmd == "hash":
        digest = hashlib.sha256(Path(a.file).read_bytes()).hexdigest()
        print("SHA-256:", digest)
    elif a.cmd == "encrypt":
        keypath = Path(a.key)
        if keypath.exists():
            key = keypath.read_bytes()
        else:
            key = AESGCM.generate_key(bit_length=256)
            keypath.write_bytes(key)
            os.chmod(keypath, 0o600)
        nonce = os.urandom(12)
        ciphertext = AESGCM(key).encrypt(nonce, Path(a.file).read_bytes(), None)
        out = Path(a.file + ".aesgcm")
        out.write_bytes(nonce + ciphertext)
        print("Archivo cifrado:", out, "| clave:", keypath, "| nonce almacenado junto al cifrado")
        print("IMPORTANTE: proteger y respaldar la clave por separado.")
    elif a.cmd == "decrypt":
        raw = Path(a.file).read_bytes()
        nonce, ciphertext = raw[:12], raw[12:]
        key = Path(a.key).read_bytes()
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
        out = Path(a.file.removesuffix(".aesgcm") + ".recovered")
        out.write_bytes(plaintext)
        print("Descifrado correcto:", out)
    elif a.cmd == "rsa-keys":
        private = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        Path(a.private).write_bytes(private.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()))
        Path(a.public).write_bytes(private.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
        os.chmod(a.private, 0o600)
        print("Par RSA generado:", a.private, "y", a.public)
    elif a.cmd == "rsa-wrap":
        pub = load_public(a.public)
        encrypted = pub.encrypt(a.text.encode(), padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(), label=None))
        Path("rsa_message.bin").write_bytes(encrypted)
        print("Mensaje cifrado con clave pública -> rsa_message.bin")
        print("Este ejemplo es solo para mensajes cortos; no cifrar archivos grandes con RSA.")
    elif a.cmd == "rsa-unlock":
        priv = load_private(a.private)
        plaintext = priv.decrypt(Path(a.file).read_bytes(), padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(), label=None))
        print("Mensaje recuperado:", plaintext.decode("utf-8"))
    elif a.cmd == "sign":
        priv = load_private(a.private)
        sig = priv.sign(Path(a.file).read_bytes(), padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        Path(a.file + ".sig").write_bytes(sig)
        print("Firma creada:", a.file + ".sig")
    elif a.cmd == "verify":
        pub = load_public(a.public)
        try:
            pub.verify(Path(a.signature).read_bytes(), Path(a.file).read_bytes(),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            print("FIRMA VÁLIDA: contenido coincide con la firma.")
        except InvalidSignature:
            print("FIRMA INVÁLIDA: el archivo cambió o la firma no corresponde.")
            raise SystemExit(2)
    elif a.cmd == "password-hash":
        password = input("Contraseña de laboratorio: ")
        encoded = PasswordHasher().hash(password)
        Path("password.hash").write_text(encoded, encoding="utf-8")
        print("Hash Argon2id guardado en password.hash")
        print("Formato codificado incluye parámetros y salt; no almacena la contraseña.")
    elif a.cmd == "password-check":
        password = input("Ingrese la contraseña a verificar: ")
        try:
            PasswordHasher().verify(a.stored_hash, password)
            print("Contraseña correcta.")
        except VerifyMismatchError:
            print("Contraseña incorrecta.")
    elif a.cmd == "ecdh-demo":
        from cryptography.hazmat.primitives.asymmetric import x25519
        from cryptography.hazmat.primitives import serialization
        alice = x25519.X25519PrivateKey.generate()
        bob = x25519.X25519PrivateKey.generate()
        a_secret = alice.exchange(bob.public_key())
        b_secret = bob.exchange(alice.public_key())
        print("Secreto Alice:", a_secret.hex())
        print("Secreto Bob:  ", b_secret.hex())
        print("¿Coinciden?:", a_secret == b_secret)
        print("El secreto compartido no se transmitió directamente.")
if __name__ == "__main__":
    main()
