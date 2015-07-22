.. _dev_application:

.. include:: ../substitutions.sub

Interacting with the core of Ecpy
=================================

This section will focus on the functionality offered by the plugins
constituting the core of the Ecpy application and how custom plugin can use
and or extend those functionalities.

.. contents::

Providing application wide commands and sharing state
-----------------------------------------------------

One usual need in plugin application is to make available to all other part of
the application some function (for example the possibility to request the use
of a driver) or to let other part of the application what is the state of a
plugin (for example a list of all the available drivers).

One could of course directly access the plugin to get those informations but
in a plugin application it is good to avoid such interferences. Those
informations are actually delegated to two plugin responsible for managing
them :

- the 'enaml.workbench.core' plugin is in charge of managing commands which are
  the equivalent of application wide available function. Each command has an
  id which is used to invoke it using the |invoke_command| of the |CorePlugin|
  (this is the only case in which one needs to access directly a plugin).
  When invoking a command one must pass a dictionary of parameters and can
  optionally pass the invoking plugin. To know what arguments the command
  expect you should look at its description in the manifest of the plugin
  contributing it.
- the 'ecpy.app.states' plugin is in charge of managing states, and allows 
  getting access to a read-only representation of some of the attributes of a
  plugin. The state of a plugin can be requested using the Command
  'ecpy.app.states.get_state' with an id parameters identifying the plugin
  constituting the state. If you need to access such a state you should
  observe the alive attribute, which becomes `False` when the plugin
  contributing the state is unregistered.
  

Declaring a Command
^^^^^^^^^^^^^^^^^^^

In order to declare a command, you must contribute a |Command| object to the
'enaml.workbench.core.commands'  extension point. A |Command| must have :

- an id which must be unique (this a dot separated name)
- a handler which is a function taking a argument an |ExecutionEvent| instance.
  The execution event allows to access the application workbench
  ('workbench' attribute) and the parameters ('parameters' attribute) passed
  to the |invoke_command| method. IF the command need to access
   the plugin you can do so easily using the workbench.
- a description which is basically the docstring of the command and should be
  formatted as such (see :doc:`style_guide`).

Declaring a State
^^^^^^^^^^^^^^^^^

In order to share the state of your plugin you must contribute a State object
to the 'ecpy.app.states.state' extension point. A |State| must have :

- an id which must be unique and can be the id of the plugin but does not have
  to.
- the names of the members of the plugin the state should reflect (as a list).
- an optional description.


Customizing application start up and closing
--------------------------------------------

In some cases, a plugin needs to perform some operation at application start up
(for example discover extension packages, or adding new logger handlers) or
some special clean up operations when the application exits. It may also need
to have a say so about whether or not the application can exit (if a measure
is running the application should not exit without a huge warning). The
'ecpy.app' plugin is responsible for handling all those possibilities. It
relies on three extension points (one for each behaviour) :

- 'ecpy.app.startup' accepts |AppStartup| contributions and deals with the start
  up of the application.
- 'ecpy.app.closing' accepts |AppClosing| contributions and deals with whether
  or not the application can be closed.
- 'ecpy.app.closed' accepts |AppClosed| contributions to run clean up operation
  before starting to unregister plugins.

.. note::

   The customisation of the start up and exit of the application should only be
   used for operations not fitting into the |Plugin.start| and |Plugin.stop|
   methods of the plugin. This fits operation that must be performed at
   application start up and cannot be deferred to plugin starting, or clean up
   operations requiring the full application to be active (ie not dependent
   only on the plugin state). 

Declaring an AppStartup extension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to customize the application start up, you need to contribute an
|AppStartup| object to the 'ecpy.app.startup' extension point. An |AppStartup|
must have :

- an id which must be unique and can be the id of the plugin but does not have
  to.
- a run attribute which must be a callable taking as single argument the
  workbench.
- a priority, which is an integer specifying when to call this start up.

.. note::

    Start up are called from **lowest** priority value to highest and by their
    order of discovery if they have the same priority. The default priority is
    20.


Declaring an AppClosing extension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to customize how the application determine whether or not it can exit,
you need to contribute an |AppClosing| object to the 'ecpy.app.closing'
extension point. An |AppClosing| must have :

- an id which must be unique and can be the id of the plugin but does not have
  to.
- a validate attribute which must be a callable taking as arguments the
  main window instance (from which the workbench can be accessed) and the
  |EventClose| associated with the attempt to close the application. If the
  plugin determine that the application should not be closed, it should call
  the |EventClose.reject| method of the |EventClose|.


Declaring an AppClosed extension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to customize the application closing, you need to contribute an
|AppClosed| object to the 'ecpy.app.closed' extension point. An |AppClosed|
must have :

- an 'id' which must be unique and can be the id of the plugin but does not
  have to.
- a 'clean' attribute which must be a callable taking as single argument the
  workbench.
- a priority, which is an integer specifying when to call this closed.

.. note::

    Closed are called from **lowest** priority value to highest and by their
    order of discovery if they have the same priority. The default priority is
    20.


Using the built in preferences manager
--------------------------------------

If any of your plugin need to retain user preferences from one application run
to the next it should use the built-in preferences management system, which
is straightforward. First your plugin should inherit from
|HasPreferencesPlugin| and should call the parent class start method in its own
start method. Second all members which should be saved should be
tagged with the 'pref' metadata (use the tag method). The value of the
metadata can be `True` or any of the values presented in :ref: XXXX. All value thus
tagged are loaded from the preference file if found, and saved when the user
request to save the preferences. Finally, you should contribute a |Preferences| object to the
'ecpy.app.preferences.plugin' extension point. A single |Preferences| object
can be contributed per plugin.

.. note::

    The preferences system saves object by writing their repr to a file so any
    object whose repr can be evaluated by literal_eval can be saved (literal_eval
    is used for security reasons).

A |Preferences| object has the following members :

- 'auto_save': list of the names of members whose update should trigger an
  automatic saving of the preferences.
- 'edit_view': an enaml Container used to edit the preferences of the plugin.
  If no such object is contributed the default templating mechanism presented
  below is used.
- 'saving_method': name of the plugin method to use to retrieve the values of
  the members which should be saved.
- 'loading_method': name of the plugin method to use to update the values of
  the saved members.

A |Preferences| object can be left blank as the default values are fine most of
the time.

Editing preferences object
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. todo:: write once implemented


Declaring dependencies
----------------------

When loading and transferring complex objects over the network, Ecpy needs to
collect all the base classes needed for reconstructing the object in an
environment lacking an active workbench. These are considered to be
build dependencies. In the same way some resources can be necessary to execute
some part of the application and need to be queried beforehand to allow the
system to run in a situation where the workbench is absent. Those are
considered to be run-time dependencies.

If your plugin introduces a new object which can, for example, be used in tasks
either as a build or as a runtime dependency you need to contribute either a
|BuildDependency| object to the 'ecpy.app.dependencies.build' extension point
or a |RuntimeDependecy| object to the 'ecpy.app.dependencies.runtime'
extension point.

.. note::

    An object introducing a new kind of build dependency should have a dep_type
    attribute that should be an atom.Constant and that must be saved if the
    object can be saved under the .ini format.

A |BuildDependency| needs:

- an 'id' which must be unique and must match the name used for dep_type
  attribute value of the object this dependency collector is meant to act on.
- 'collect': a method getting the build dependency of an object and
  identifying its runtime dependencies.

A |RuntimeDependecy| needs:

- an 'id' which must be unique.
- 'collect': a method getting the runtime dependency of an object.


Customizing logging
-------------------

By default Ecpy use two logs:

- a log collecting all levels and directed to a file (in the application folder
  under logs), which is rotated daily or every time the application starts.
- a log collecting INFO log and above and stored in a string with a max of 1000
  lines. This string is meant to be used for displaying the log in the GUI, and
  is available from the state of the log plugin ('ecpy.app.logging').

If you need to add handlers, formatters or filters, you should do so in the
|Plugin.start| method of your plugin by calling the corresponding commands
:ref: XXXX .


Contributing to the application interface
-----------------------------------------

Adding entries in the main window menu bar
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Plugins can also add new entries to the menu bar of the application main
window. To do so they should contribute |MenuItem| and |ActionItem| to the
'enaml.workbench.ui' plugin.

Providing new workspaces
^^^^^^^^^^^^^^^^^^^^^^^^

.. todo:: write
