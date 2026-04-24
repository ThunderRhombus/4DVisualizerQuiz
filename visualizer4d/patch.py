import os

files = ['MAINWireframe.py', 'MAINWShell.py']

for file in files:
    with open(file, 'r') as f:
        content = f.read()
    
    # 1. Add main() wrapper
    content = content.replace('pygame.init()', 'from origin_viewer import spawn_origin_viewer\ndef main():\n    shared_arr = spawn_origin_viewer()\n    pygame.init()')
    
    # 2. Indent everything after pygame.init
    lines = content.split('\n')
    out = []
    in_main = False
    skip_hastext = False
    for line in lines:
        if line.startswith('def main():'):
            in_main = True
            
        if in_main and line.startswith('pygame.init()'):
            out.append('    pygame.init()')
            continue
            
        if in_main and not line.startswith('def main()') and not line.startswith('    shared_arr'):
            line = '    ' + line if line.strip() else line
            
        if 'if hasattr(shape, \'hastext\') and shape.hastext:' in line:
            skip_hastext = True
            # remove 'for shape in shapes:' and comments
            assert out[-1].strip() == 'for shape in shapes:'
            out.pop()
            if out[-1].strip().startswith('#'): out.pop()
            continue
            
        if skip_hastext:
            if 'screen.blit(text_surf' in line:
                skip_hastext = False
            continue
            
        if 'shapes = [tess, axis]' in line:
            out.append('    shapes = [tess]')
            continue
            
        if 'axis = wAxis' in line:
            continue
            
        if 'pygame.display.flip()' in line:
            # We must be careful about MAINWShell.py vs MAINWireframe.py ortho
            if file == 'MAINWShell.py':
                out.append('        shared_arr[:] = [yaw, pitch, roll, dip, tuck, skew, 0.001]')
            else:
                out.append('        shared_arr[:] = [yaw, pitch, roll, dip, tuck, skew, ortho]')
            out.append(line)
            continue
            
        out.append(line)
        
    out.append("if __name__ == '__main__':")
    out.append("    main()")
    
    with open(file, 'w') as f:
        f.write('\n'.join(out))
