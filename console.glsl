---vertex shader---------------------------------------------------------------
$HEADER$

attribute vec2 vCenter;
attribute float vScale;
attribute vec3 vColor;
attribute float isTexFlag;

varying float isTex;

void main() {
    tex_coord0 = vTexCoords0;
    frag_color = vec4(vColor.rgb, 1.0);
    isTex = isTexFlag;

    mat4 move_mat = mat4(
        1.0, 0.0, 0.0, vCenter.x,
        0.0, 1.0, 0.0, vCenter.y,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    );
    vec4 pos = vec4(vPosition.xy, 0.0, 1.0) * move_mat;
    gl_Position = projection_mat * modelview_mat * pos;
}

---fragment shader-------------------------------------------------------------
$HEADER$
uniform vec3 TEX_BG_COLOR = vec3(0.0, 0.0, 0.0);
varying float isTex;

void main() {
    if (isTex < 1.0) {
        gl_FragColor = frag_color;
    }
    else {
        gl_FragColor = frag_color * texture2D(texture0, tex_coord0);
        if (gl_FragColor.rgb == TEX_BG_COLOR) {
            discard;
        }
    }
}
