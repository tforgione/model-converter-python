varying vec3 fNormal;

vec3 ambientLight = vec3(0.2,0.2,0.2);
vec3 directionnalLight = normalize(vec3(10,5,7));
vec3 directionnalLightFactor = vec3(0.5,0.5,0.5);


void main() {

    vec3 ambientFactor = ambientLight;
    vec3 lambertFactor = max(vec3(0.0,0.0,0.0), dot(directionnalLight, fNormal) * directionnalLightFactor);

    gl_FragColor = vec4(ambientFactor + lambertFactor, 1.0);
}
