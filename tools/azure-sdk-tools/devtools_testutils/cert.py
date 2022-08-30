from typing import List

def create_combined_bundle(cert_files: List[str], output_location: str) -> None:
   """
   Combines a list of ascii-encoded PEM certificates into one bundle.
   """
   combined_cert_strings: List[str] = []
   
   for cert_path in cert_files:
      with open(cert_path, 'r') as f:
         combined_cert_strings.extend(f.readlines())
      
   with open(output_location, 'w') as f:
      f.writelines(combined_cert_strings)
