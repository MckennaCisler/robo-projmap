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
GLuint indexbuffer;

// left to right
static const unsigned int g_indices_data[] = {
        3, 4, 5,
        0, 1, 2,
        6, 7, 8,
};

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

/**
 * Takes in (int height, int width, np.ndarray projector matrix, output monitor). 
 * The projector matrix must be 3x3, and output monitor can be negative for windowed mode.
 * Returns True on success, False otherwise
 */
PyObject *start(PyObject *self, PyObject *args) {
    // Extract Python args
    int width = 1366;
    int height = 768;
    // TODO: matrix
    int monitor_index = -1;

    // Initialise GLFW
    if( !glfwInit() ) {
        fprintf( stderr, "Failed to initialize GLFW\n" );
        Py_RETURN_FALSE;
    }

    glfwWindowHint(GLFW_SAMPLES, 4);
    glfwWindowHint(GLFW_RESIZABLE,GL_FALSE);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // To make MacOS happy; should not be needed
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Open a window and create its OpenGL context
    window = glfwCreateWindow( width, height, "Projector View", NULL, NULL);
    if( window == NULL ) {
        fprintf( stderr, "Failed to open GLFW window. If you have an Intel GPU, they are not 3.3 compatible. Try the 2.1 version of the tutorials.\n" );
        glfwTerminate();
        Py_RETURN_FALSE;
    }
    glfwMakeContextCurrent(window);

    // Set the window to be fullscreened in the given monitor
    if (monitor_index >= 0) {
        int count;
        GLFWmonitor** monitors = glfwGetMonitors(&count);
        if (monitor_index >= count) {
            fprintf(stderr, "Not enough monitors (%d) to project to monitor at index %d\n", count, monitor_index);
            Py_RETURN_FALSE;
        }
        glfwSetWindowMonitor(window, monitors[monitor_index], 0, 0, width, height, GLFW_DONT_CARE);
    }

    // Initialize GLEW
    glewExperimental = true;
    if (glewInit() != GLEW_OK) {
        fprintf(stderr, "Failed to initialize GLEW\n");
        glfwTerminate();
		Py_RETURN_FALSE;
    }

    // Ensure we can capture the escape key being pressed below
    glfwSetInputMode(window, GLFW_STICKY_KEYS, GL_TRUE);

    // Dark blue background
    glClearColor(0.0f, 0.0f, 0.4f, 0.0f);

    // Setup vertex arrays
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

    // Generate a buffer for the vertices (XYD points)
    glGenBuffers(1, &vertexbuffer);
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer);
    glBufferData(GL_ARRAY_BUFFER, sizeof(g_vertex_buffer_data), g_vertex_buffer_data, GL_STATIC_DRAW);

    // Generate a buffer for the indices of the triangle points
    glGenBuffers(1, &indexbuffer);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexbuffer);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(g_indices_data), g_indices_data, GL_STATIC_DRAW);

    Py_RETURN_TRUE;
}

/**
 * Takes in (np.ndarray color values, np.ndarray xyd points, np.ndarray triangle indices). 
 * The color array is Nx3, while the points and indices are both N-length one-dimensional arrays,
 * where N is the width*height of the image.
 * Returns true when the window was closed.
 */
PyObject *draw_frame(PyObject *self, PyObject *args) {
    // TODO: read args

    // TODO: populate buffers here instead of on start

    glClear(GL_COLOR_BUFFER_BIT);

    // Use our shader
    glUseProgram(programID);
    glUniformMatrix4fv(MatrixID, 1, GL_FALSE, &MVP[0][0]);

    // enable vertices attribute buffer
    glEnableVertexAttribArray(0);
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer);
    glVertexAttribPointer(
            0,                  // attribute 0. No particular reason for 0, but must match the layout in the shader.
            3,                  // size (3-space)
            GL_FLOAT,           // type
            GL_FALSE,           // normalized?
            0,                  // stride
            (void*)0            // array buffer offset
    );

    // Draw the triangles using the vertex indices in the indices data
    glDrawElements(
        GL_TRIANGLES,               // mode
        sizeof(g_indices_data),     // count
        GL_UNSIGNED_INT,            // type
        (void*)0                    // element array buffer offset
    );

    glDisableVertexAttribArray(0);

    // Swap buffers
    glfwSwapBuffers(window);

    // Check for exit keypresses
    glfwPollEvents();
	if (glfwGetKey(window, GLFW_KEY_ESCAPE ) != GLFW_PRESS && glfwWindowShouldClose(window) == 0) {
		Py_RETURN_FALSE;
	} else {
		Py_RETURN_TRUE;
	}
}

/**
 * Stops rendering
 */
PyObject *stop(PyObject *self, PyObject *args) {
    glfwTerminate();
	Py_RETURN_NONE;
}

static PyMethodDef ProjectMethods[] = {
	{"start",  start, METH_VARARGS, "Starts the projector display at the given resolution, using the given camera->projector conversion matrix"},
	{"draw_frame",  draw_frame, METH_VARARGS, "Transforms the given frame and corresponding triangle indices into a mesh which is then projected and displayed"},
	{"stop",  stop, METH_NOARGS, "Stops the projector display"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


static struct PyModuleDef projectmodule = {
    PyModuleDef_HEAD_INIT,
    "project",   /* name of module */
    "basic doc string", /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    ProjectMethods
};


PyMODINIT_FUNC PyInit_project(void)
{
    import_array();
    return PyModule_Create(&projectmodule);
}
