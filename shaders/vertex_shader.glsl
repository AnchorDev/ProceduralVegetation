#version 330 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec3 aColor;

out vec3 FragPos;
out vec3 FragNormal;
out vec3 FragColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    vec4 worldPos = model * vec4(aPos, 1.0);
    FragPos = worldPos.xyz;

    // Transformacja normalnych
    mat3 normalMatrix = transpose(inverse(mat3(model)));
    FragNormal = normalize(normalMatrix * aNormal);

    FragColor = aColor;

    gl_Position = projection * view * worldPos;
}
