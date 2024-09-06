from cryptography.hazmat.primitives.serialization import load_pem_private_key
from securesystemslib.signer import CryptoSigner
from in_toto.models.layout import Layout
from in_toto.models.metadata import Envelope
# https://github.com/in-toto/in-toto/issues/663
from in_toto.models._signer import load_public_key_from_file
def main():
  # Load SecOp's private key to later sign the layout
  with open("secop", "rb") as f:
    key_secop = load_pem_private_key(f.read(), None)

  signer_secop = CryptoSigner(key_secop)
  # Fetch and load Senthil's public keys
  # to specify that they are authorized to perform certain step in the layout
  key_senthil  = load_public_key_from_file("../functionary_senthil/senthil.pub") 
  key_packer  = load_public_key_from_file("../functionary_packer/packer.pub")

  layout = Layout.read({
      "_type": "layout",
      "keys": {
          key_senthil["keyid"]: key_senthil,
          key_packer["keyid"]: key_packer,
      },
      "steps": [{
          "name": "clone",
          "expected_materials": [],
          "expected_products": [
              ["CREATE", "manifest/authorization_server-service.yaml"],
              ["CREATE", "manifest/authorization-server-deployment.yaml"],
              ["CREATE", "manifest/client-deployment.yaml"],
              ["CREATE", "manifest/client-service.yaml"],
              ["CREATE", "manifest/mysql-cm0-configmap.yaml"],
              ["CREATE", "manifest/mysql-deployment.yaml"],
              ["CREATE", "manifest/mysql-service.yaml"],
              ["CREATE", "manifest/resource_server-service.yaml"],
              ["CREATE", "manifest/resource-server-deployment.yaml"],
              ["DISALLOW", "*"]
          ],
          "pubkeys": [key_senthil["keyid"]],
          "expected_command": [
              "cp",
              "-pr",
              "../../k8s/manifest/",
              ".",
          ],
          "threshold": 1,
        },{
          "name": "update-version",
          "expected_materials": [["MATCH", "manifest/*", "WITH", "PRODUCTS",
                                "FROM", "clone"], ["DISALLOW", "*"]],
          "expected_products": [
              ["CREATE", "manifest/authorization_server-service.yaml"],
              ["CREATE", "manifest/authorization-server-deployment.yaml"],
              ["MODIFY", "manifest/client-deployment.yaml"],
              ["CREATE", "manifest/client-service.yaml"],
              ["CREATE", "manifest/mysql-cm0-configmap.yaml"],
              ["CREATE", "manifest/mysql-deployment.yaml"],
              ["CREATE", "manifest/mysql-service.yaml"],
              ["CREATE", "manifest/resource_server-service.yaml"],
              ["CREATE", "manifest/resource-server-deployment.yaml"],
              ["DISALLOW", "*"]
          ],
          "pubkeys": [key_senthil["keyid"]],
          "expected_command": [],
          "threshold": 1,
        },{
          "name": "package",
          "expected_materials": [
            ["MATCH", "manifest/*", "WITH", "PRODUCTS", "FROM",
             "update-version"], ["DISALLOW", "*"],
          ],
          "expected_products": [
              ["CREATE", "manifest.tar.gz"], ["DISALLOW", "*"],
          ],
          "pubkeys": [key_packer["keyid"]],
          "expected_command": [
              "tar",
              "--exclude",
              ".git",
              "-zcvf",
              "manifest.tar.gz",
              "manifest",
          ],
          "threshold": 1,
        }],
      "inspect": [{
          "name": "untar",
          "expected_materials": [
              ["MATCH", "manifest.tar.gz", "WITH", "PRODUCTS", "FROM", "package"],
              # FIXME: If the routine running inspections would gather the
              # materials/products to record from the rules we wouldn't have to
              # ALLOW other files that we aren't interested in.
              ["ALLOW", ".keep"],
              ["ALLOW", "secop.pub"],
              ["ALLOW", "root.layout"],
              ["ALLOW", "*.link"],
              ["DISALLOW", "*"]
          ],
          "expected_products": [
              ["MATCH", "manifest/client-deployment.yaml", "WITH", "PRODUCTS", "FROM", "update-version"],
              # FIXME: See expected_materials above
              ["ALLOW", "manifest/authorization_server-service.yaml"],
              ["ALLOW", "manifest/authorization-server-deployment.yaml"],
              ["ALLOW", "manifest/client-service.yaml"],
              ["ALLOW", "manifest/mysql-cm0-configmap.yaml"],
              ["ALLOW", "manifest/mysql-deployment.yaml"],
              ["ALLOW", "manifest/mysql-service.yaml"],
              ["ALLOW", "manifest/resource_server-service.yaml"],
              ["ALLOW", "manifest/resource-server-deployment.yaml"],
              ["ALLOW", "manifest/.git/*"],
              ["ALLOW", "manifest.tar.gz"],
              ["ALLOW", ".keep"],
              ["ALLOW", "secop.pub"],
              ["ALLOW", "root.layout"],
              ["ALLOW", "*.link"],
              ["DISALLOW", "*"]
          ],
          "run": [
              "tar",
              "xzf",
              "manifest.tar.gz",
          ]
        }],
  })

  metadata = Envelope.from_signable(layout)

  # Sign and dump layout to "root.layout"
  metadata.create_signature(signer_secop)
  metadata.dump("root.layout")
  print('Created demo in-toto layout as "root.layout".')

if __name__ == '__main__':
  main()
