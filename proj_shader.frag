#version 330 core

in vec3 colorOut; // color from vertex shader
out vec3 color; // output color

void main()
{
	color = colorOut;
}
