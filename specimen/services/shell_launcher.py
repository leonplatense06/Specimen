import os
import subprocess
from pathlib import Path
from typing import Dict, Any

class ShellLauncher:
    def launch(self, shell: str, env: Dict[str, str], session_id: str, temp_dir: Path) -> subprocess.Popen:
        """
        Lanza la shell especificada configurando las variables de entorno y
        el prompt de inicialización temporal. Retorna el objeto Popen.
        """
        shell_name = Path(shell).name
        full_env = {**os.environ, **env}
        
        # Asegurar que el directorio temp exista
        temp_dir.mkdir(parents=True, exist_ok=True)

        if shell_name == "bash":
            script_path = self._write_bash_rc(env, session_id, temp_dir)
            return subprocess.Popen([shell, "--rcfile", str(script_path)], env=full_env)

        elif shell_name == "zsh":
            zdotdir = self._write_zsh_rc(env, session_id, temp_dir)
            return subprocess.Popen([shell], env={**full_env, "ZDOTDIR": str(zdotdir)})

        elif shell_name == "fish":
            init_cmds = self._build_fish_init(env)
            return subprocess.Popen([shell, "--init-command", init_cmds], env=full_env)

        else:
            # Fallback a bash con advertencia (el llamador se encarga de la advertencia)
            script_path = self._write_bash_rc(env, session_id, temp_dir)
            return subprocess.Popen(["bash", "--rcfile", str(script_path)], env=full_env)

    def _write_bash_rc(self, env: Dict[str, str], session_id: str, temp_dir: Path) -> Path:
        script_path = temp_dir / f"{session_id}.sh"
        lines = []
        
        # Cargar configuración original del usuario
        user_bashrc = Path.home() / ".bashrc"
        if user_bashrc.exists():
            lines.append(f"source {user_bashrc}")
            
        # Exportar variables de Specimen
        for k, v in env.items():
            lines.append(f"export {k}=\"{v}\"")
            
        # Configurar prompt
        spec_name = env.get("SPEC_NAME", "spec")
        lines.append(f"export PS1=\"({spec_name}) $PS1\"")
        
        script_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return script_path

    def _write_zsh_rc(self, env: Dict[str, str], session_id: str, temp_dir: Path) -> Path:
        zdotdir = temp_dir / f"{session_id}_zsh"
        zdotdir.mkdir(parents=True, exist_ok=True)
        zshrc_path = zdotdir / ".zshrc"
        lines = []
        
        # Cargar configuración original del usuario
        user_zshrc = Path.home() / ".zshrc"
        if user_zshrc.exists():
            lines.append(f"source {user_zshrc}")
            
        # Exportar variables
        for k, v in env.items():
            lines.append(f"export {k}=\"{v}\"")
            
        # Configurar prompt
        spec_name = env.get("SPEC_NAME", "spec")
        lines.append(f"export PROMPT=\"({spec_name}) $PROMPT\"")
        lines.append(f"export PS1=\"({spec_name}) $PS1\"")
        
        zshrc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return zdotdir

    def _build_fish_init(self, env: Dict[str, str]) -> str:
        cmds = []
        
        for k, v in env.items():
            if k == "PATH":
                # En Fish, el PATH se define con espacios en lugar de ':'
                bin_path = v.split(":")[0]
                cmds.append(f"set -gx PATH \"{bin_path}\" \\$PATH")
            else:
                cmds.append(f"set -gx {k} \"{v}\"")
                
        # Redefinir fish_prompt para anteponer el nombre del specimen
        spec_name = env.get("SPEC_NAME", "spec")
        cmds.append("functions -c fish_prompt _original_fish_prompt")
        cmds.append("function fish_prompt")
        cmds.append(f"    printf '({spec_name}) '")
        cmds.append("    _original_fish_prompt")
        cmds.append("end")
        
        return "; ".join(cmds)
