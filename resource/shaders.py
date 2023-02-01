vertex_shader = '''
                #version 330
                
                uniform mat4 Mvp;
                
                in vec3 in_position;
                in vec3 in_normal;
                in vec2 in_texcoord_0;
                
                out vec3 v_vert;
                out vec3 v_norm;
                out vec2 v_text;
                
                void main() {
                    v_vert = in_position;
                    v_norm = in_normal;
                    v_text = in_texcoord_0;
                    gl_Position = Mvp * vec4(in_position, 1.0);
                }
            '''
fragment_shader = '''
                #version 330
                
                uniform sampler2D Texture;
                uniform vec4 Color;
                uniform vec3 Light;
                
                in vec3 v_vert;
                in vec3 v_norm;
                in vec2 v_text;
                
                out vec4 f_color;
                
                void main() {
                    float lum = -dot(normalize(v_norm), normalize(v_vert + Light));
                    lum = acos(lum) / 3.14159265;
                    lum = clamp(lum, 0.0, 1.0);
                    lum = lum * lum;
                    lum = smoothstep(0.0, 1.0, lum);
                    lum *= smoothstep(0.0, 80.0, v_vert.z) * 0.3 + 0.7;
                    lum = lum * 0.8 + 0.2;
                    
                    vec3 color = texture(Texture, v_text).rgb;
                    color = color * (1.0 - Color.a) + Color.rgb * Color.a;
                    f_color = vec4(color * lum, Color.a);
                }
            '''
