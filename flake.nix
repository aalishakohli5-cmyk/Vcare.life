{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };
  outputs = { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"  "aarch64-linux"
        "x86_64-darwin" "aarch64-darwin"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f {
        inherit system;
        pkgs = nixpkgs.legacyPackages.${system};
      });
    in
  {
    devShells = forAllSystems ({ pkgs, ... }: {
      default = pkgs.mkShell {
        packages = with pkgs; [
          just
          bun
          vtsls
        ];
        shellHook = ''
          echo "⟡ Bun JS : v$(bun --version)"
          echo "────୨ৎ────"
        '';
      };
    });
  };
}
