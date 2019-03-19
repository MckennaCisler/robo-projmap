#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdlib.h>

#include <GL/glew.h>

#include <GLFW/glfw3.h>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include "common/shader.hpp"

#include <time.h>
using namespace glm;


GLFWwindow* window;
GLuint VertexArrayID;
GLuint vertexbuffer;
GLuint programID;
GLint MatrixID;
glm::mat4 MVP;


static const GLfloat g_vertex_buffer_data[] = {
        -1.0f, -1.0f, 0.0f,
        1.0f, -1.0f, 0.0f,
        0.0f,  1.0f, 0.0f,
        -3.0f, -1.0f, 0.0f,
        -1.0f, -1.0f, 0.0f,
        -2.0f,  1.0f, 0.0f,
        1.0f, -1.0f, 0.0f,
        3.0f, -1.0f, 0.0f,
        2.0f,  1.0f, 0.0f,
};

PyObject *start(PyObject *self, PyObject *args) {
    // Initialise GLFW
    if( !glfwInit() ) {
        fprintf( stderr, "Failed to initialize GLFW\n" );
        Py_RETURN_NONE;;
    }

    glfwWindowHint(GLFW_SAMPLES, 4);
    glfwWindowHint(GLFW_RESIZABLE,GL_FALSE);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // To make MacOS happy; should not be needed
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Open a window and create its OpenGL context
    window = glfwCreateWindow( 1366, 768, "Playground", NULL, NULL);
    if( window == NULL ) {
        fprintf( stderr, "Failed to open GLFW window. If you have an Intel GPU, they are not 3.3 compatible. Try the 2.1 version of the tutorials.\n" );
        glfwTerminate();
        Py_RETURN_NONE;
    }
    glfwMakeContextCurrent(window);

    // Initialize GLEW
    glewExperimental = true;
    if (glewInit() != GLEW_OK) {
        fprintf(stderr, "Failed to initialize GLEW\n");
        glfwTerminate();
		Py_RETURN_NONE;
    }

    // Ensure we can capture the escape key being pressed below
    glfwSetInputMode(window, GLFW_STICKY_KEYS, GL_TRUE);

    // Dark blue background
    glClearColor(0.0f, 0.0f, 0.4f, 0.0f);

    glGenVertexArrays(1, &VertexArrayID);
    glBindVertexArray(VertexArrayID);

    // Create and compile our GLSL program from the shaders
    programID = LoadShaders( "shader.vert", "shader.frag" );

    // Get a handle for our "MVP" uniform
    MatrixID = glGetUniformLocation(programID, "MVP");

    MVP[1][0] = 0.2f;
    MVP[0][1] = -0.2f;
    MVP[0][0] = 1.0f;
    MVP[1][1] = 1.0f;
    MVP[2][2] = 1.0f;
    MVP[3][3] = 4.0f;

    glGenBuffers(1, &vertexbuffer);    // Close OpenGL window and terminate GLFW
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer);
    glBufferData(GL_ARRAY_BUFFER, sizeof(g_vertex_buffer_data), g_vertex_buffer_data, GL_STATIC_DRAW);
	Py_RETURN_NONE;
}

PyObject *draw_frame(PyObject *self, PyObject *args) {
    glClear(GL_COLOR_BUFFER_BIT);

    // Use our shader
    glUseProgram(programID);
    glUniformMatrix4fv(MatrixID, 1, GL_FALSE, &MVP[0][0]);


    // 1rst attribute buffer : vertices
    glEnableVertexAttribArray(0);
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer);
    glVertexAttribPointer(
            0,                  // attribute 0. No particular reason for 0, but must match the layout in the shader.
            3,                  // size
            GL_FLOAT,           // type
            GL_FALSE,           // normalized?
            0,                  // stride
            (void*)0            // array buffer offset
    );


    // Draw Traingles
    glDrawArrays(GL_TRIANGLES, 0, 9);

    glDisableVertexAttribArray(0);

    // Swap buffers
    glfwSwapBuffers(window);
    glfwPollEvents();

	if (glfwGetKey(window, GLFW_KEY_ESCAPE ) != GLFW_PRESS && glfwWindowShouldClose(window) == 0) {
		Py_RETURN_FALSE;
	} else {
		Py_RETURN_TRUE;
	}
}

PyObject *end(PyObject *self, PyObject *args) {
    glfwTerminate();
	Py_RETURN_NONE;
}

static PyMethodDef DrawMethods[] = {
	{"start",  start, METH_NOARGS, "Testing numpy"},
	{"draw_frame",  draw_frame, METH_NOARGS, "Testing numpy"},
	{"end",  end, METH_NOARGS, "Testing numpy"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


static struct PyModuleDef drawmodule = {
    PyModuleDef_HEAD_INIT,
    "draw",   /* name of module */
    "basic doc string", /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    DrawMethods
};


PyMODINIT_FUNC PyInit_draw(void)
{
    import_array();
    return PyModule_Create(&drawmodule);
}
