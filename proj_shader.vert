#version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec3 vertexPosition_modelspace;

// Input color data (per vertex), passed straight through to the fragment shader
layout(location = 1) in vec3 colorIn;
out vec3 colorOut;

// Values that stay constant for the whole mesh.
uniform mat4 MVP;

void main() {

    colorOut = colorIn;

	// Output position of the vertex, in clip space : MVP * position
	gl_Position =  MVP * vec4(vertexPosition_modelspace,1);

}

