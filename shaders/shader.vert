varying vec3 fNormal;

void main() {
    fNormal = gl_Normal;
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
