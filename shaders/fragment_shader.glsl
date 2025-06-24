#version 330 core

in vec3 FragPos;
in vec3 FragNormal;
in vec3 FragColor;

out vec4 FragOutput;

uniform vec3 lightDir;   // kierunek padania światła (znormalizowany)
uniform vec3 lightColor; // kolor światła (np. 1.0, 1.0, 0.9)

void main()
{
    vec3 norm = normalize(FragNormal);
    vec3 light = normalize(-lightDir); // odwracamy, bo to "padanie" światła

    float diff = max(dot(norm, light), 0.0); // model Lambertowski
    vec3 diffuse = diff * lightColor * FragColor;

    vec3 ambient = 0.2 * FragColor;

    vec3 result = ambient + diffuse;
    FragOutput = vec4(result, 1.0);
}
