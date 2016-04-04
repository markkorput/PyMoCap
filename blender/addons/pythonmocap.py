# blender-addon info
bl_info = {
    "name": "PyMoCap",
    "author": "Short Notion (Mark van de Korput)",
    "version": (1, 0, 0),
    "blender": (2, 75, 0),
    "location": "View3D > T-panel > Object Tools",
    "description": "Use real time NatNet MoCap data in your blender game project",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"}

# blender python interface
import bpy
from bpy.app.handlers import persistent
import logging
import mathutils
import os.path

# MoCapBridge package
from pymocap.manager import Manager
from pymocap.readers.natnet_reader import NatnetReader
from pymocap.readers.natnet_file_reader import NatnetFileReader


# lgobal shared manager
manager = None

def setup():
    logging.getLogger().debug('PyMoCap.setup')
    global manager
    manager = Manager()
    bpy.app.handlers.game_post.append(destroy)

# This method should be called by a controller in the blender object's
# game logic and that controller should be triggered by an 'always' sensor,
# with TRUE level triggering enabled (Pulse mode) so it gets called every game-loop iteration
def update(controller):
    owner = controller.owner
    PyMoCap.for_owner(owner).update()

@persistent
def destroy(scene):
    logging.getLogger().debug('PyMoCap.destroy')

    for instance in PyMoCap._instances_by_owner.values():
        instance.destroy()
        PyMoCap._instances_by_owner = {}

class PyMoCap:
    _instances_by_owner = {}

    def for_owner(owner):
        if owner in PyMoCap._instances_by_owner:
            return PyMoCap._instances_by_owner[owner]

        # Create new instance
        inst = PyMoCap(owner)
        # Store it so it can be found next time
        PyMoCap._instances_by_owner[owner] = inst
        return inst

    def __init__(self, owner):
        global manager
        self.owner = owner

        self.config = bpy.data.objects[self.owner.name].pyMoCapConfig
        self.natnet_config = bpy.data.objects[self.owner.name].pyMoCapNatnetConfig
        self.natnet_file_config = bpy.data.objects[self.owner.name].pyMoCapNatnetFileConfig
        self.spawner_config = bpy.data.objects[self.owner.name].pyMoCapSpawnerConfig
        self.rb_follower_config = bpy.data.objects[self.owner.name].pyMoCapRbFollowerConfig

        self.manager = manager
        self.newFrame = False
        self.spawnedObjects = []

        if not self.config.enabled:
            return

        if self.natnet_config.enabled:
            self.natnet_reader = NatnetReader(manager=self.manager, host=self.natnet_config.host, multicast=self.natnet_config.multicast, port=self.natnet_config.port)

        if self.natnet_file_config.enabled:
            self.file_reader = NatnetFileReader({
                'path': bpy.path.abspath(self.natnet_file_config.file),
                'manager': self.manager,
                'loop': self.natnet_file_config.loop,
                'sync':self.natnet_file_config.sync})

        self.manager.frameEvent += self.onFrame

    def __del__(self):
        self.destroy()

    def destroy(self):
        if hasattr(self, 'natnet_reader'):
            self.natnet_reader.stop()

        if hasattr(self, 'file_reader'):
            self.file_reader.stop()

    def update(self):
        if not self.config.enabled:
            return

        if self.natnet_config.enabled:
            self.natnet_reader.update()

        if self.natnet_file_config.enabled:
            self.file_reader.update()
            # print("NatnetFileReader time: {0}".format(self.reader.getTime()))

        if self.newFrame:
            self._processFrame(self.manager.frame)
            self.newFrame = False

    def onFrame(self, frame, manager):
        # add frame to queue for processing in update method
        self.newFrame = True

    def _processFrame(self, frame):
        # spawn/unspawn objects so there is exactly one instance
        # of the specified object for each rigid body in the frame
        if self.spawner_config.enabled:
            # remove rigid bodies that have been removed
            for i in range(len(self.spawnedObjects) - len(frame.rigid_bodies)):
                logging.getLogger().debug("TODO: remove spawned object")
                self.spawnedObjects[-1].endObject()
                self.spawnedObjects.pop()

            # spawn objects
            for i in range(len(frame.rigid_bodies) - len(self.spawnedObjects)):
                logging.getLogger().debug("Spawning MoCap object")
                object = self.owner.scene.addObject(self.spawner_config.object, self.spawner_config.object)
                object.setParent(self.owner)
                self.spawnedObjects.append(object)

        # at this point self.spawnedObjects should have the same amount of objects
        # as there are rigid bodies in the frame
        for idx, rigid_body in enumerate(frame.rigid_bodies):
            # re-config all objects with updated rigid bodies data
            if self.spawner_config.enabled:
                obj = self.spawnedObjects[idx]
                obj.localPosition = rigid_body.position
                obj.localOrientation = mathutils.Quaternion(rigid_body.orientation)

            # update object if it is following the current rigid body
            if self.rb_follower_config.enabled:
                if int(self.rb_follower_config.rbindex) == idx or (int(rigid_body.id) == int(self.rb_follower_config.rbid) or (int(self.rb_follower_config.rbid) == -1 and idx==0)):
                    self.owner.localPosition = rigid_body.position
                    self.owner.localOrientation = rigid_body.orientation


# This class is in charge of the blender UI config panel
class Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "PyMoCap"
    bl_idname = "OBJECT_pymocap"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw_header(self, context):
      layout = self.layout
      config = context.object.pyMoCapConfig
      layout.prop(config, "enabled", text='')

    def draw(self, context):
        layout = self.layout
        config = context.object.pyMoCapConfig

        if config.enabled == True:
            self.draw_natnet(context)
            self.draw_natnet_file(context)
            self.draw_spawner(context)
            self.draw_rb_follower(context)

            obj = PyMoCapObj(context.object)
            # game logic connection not complete; inform user and provide
            # buttons to auto-configure
            if obj.gameLogicConnection() == True:
              layout.row().label(text='Game logic: OK')
            else:
              msgs = []

              if obj.sensor() == None:
                msgs.append('Sensor: NO')
              else:
                msgs.append('Sensor: OK')

              if obj.controller() == None:
                msgs.append('Controller: NO')
              else:
                msgs.append('Controller: OK')

              msgs.append('Connection: NO')
              layout.row().label(text=', '.join(msgs))
              layout.row().operator("object.pymocap_config_game_logic", text="Configure")

    def draw_natnet(self, context):
        config = context.object.pyMoCapNatnetConfig
        self.layout.row().prop(config, 'enabled', text='Natnet Receiver')
        if config.enabled:
            box = self.layout.box()
            box.row().prop(config, "host")
            box.row().prop(config, "multicast")
            box.row().prop(config, "port")

    def draw_natnet_file(self, context):
        config = context.object.pyMoCapNatnetFileConfig
        obj = PyMoCapObj(context.object)

        self.layout.row().prop(config, 'enabled', text='Natnet File Reader')
        if config.enabled:
            box = self.layout.box()
            box.row().prop(config, "file")
            if not obj.natnetFileExists():
                box.row().label(text='File could not be found')
            r = box.row()
            r.prop(config, "loop")
            r.prop(config, "sync")

    def draw_spawner(self, context):
        config = context.object.pyMoCapSpawnerConfig
        self.layout.row().prop(config, 'enabled', text='Spawner')
        if config.enabled:
            box = self.layout.box().row().prop(config, "object")

    def draw_rb_follower(self, context):
        config = context.object.pyMoCapRbFollowerConfig
        self.layout.row().prop(config, 'enabled', text='RigidBody Follower')
        if config.enabled:
            box = self.layout.box()
            r = box.row()
            r.prop(config, "rbid")
            txt = 'Disabled' if config.rbid == 0 else 'To disable, enter 0 (zero)'
            r.label(txt)
            r = box.row()
            txt = 'Disabled' if config.rbindex == -1 else 'To disable, enter -1'
            r.prop(config, "rbindex")
            r.label(txt)
            if config.rbid != 0 and config.rbindex != -1:
                box.row().label('Only one of the two should be enabled')



# This class provides PyMoCap-related information (read-only)
# about a blender object (not a game engine object)
class PyMoCapObj:
    """docstring for """
    def __init__(self, object):
        self.object = object

    def gameLogicConnection(self):
        # if there is no valid sensor, then there can be no connection either
        if self.sensor() == None:
            return False

        # see if the sensor is hooked up to our controller
        # that is assuming there IS a valid controller
        for controller in self.sensor().controllers:
            if controller == self.controller():
                return True

        # no dice
        return False

    def sensor(self):
        # loop through all of this object's game logic sensors
        for sensor in self.object.game.sensors:
            # find one that is appropriately configured
            if sensor.type == 'ALWAYS' and sensor.use_pulse_false_level == False and sensor.use_pulse_true_level == True:
                # return it if found
                return sensor
        # doesn't exist (yet)
        return None

    # returns a controller reference to a appropriaely configured python module controller
    def controller(self):
        for controller in self.object.game.controllers:
            if controller.type == 'PYTHON' and controller.mode == 'MODULE' and controller.module == 'pythonmocap.update':
                return controller
        return None

    def fullNatnetFilePath(self):
        return bpy.path.abspath(self.object.pyMoCapNatnetFileConfig.file)

    def natnetFileExists(self):
        return os.path.isfile(self.fullNatnetFilePath())

class PyMoCapConfigGameLogicOperator(bpy.types.Operator):
    bl_idname = "object.pymocap_config_game_logic"
    bl_label = "Creates the game logic sensor and controller that requires PyMoCap to work"
    bl_description = "Creates an Always sensor and a Python module controller and links them"

    # @classmethod
    # def poll(cls, context):
    #     return True

    def execute(self, context):
      obj = PyMoCapObj(context.object)
      if obj.controller() == None:
        self.createController(context)

      if obj.sensor() == None:
        self.createSensor(context)

      if obj.gameLogicConnection() != True:
        # create the connection
        print("PyMoCap creating game logic links")
        obj.sensor().link(obj.controller())

      return {'FINISHED'}

    def createController(self, context):
        print("PyMoCap creating Python module controller")
        # create empty PYTHON controller
        bpy.ops.logic.controller_add(type='PYTHON')
        # get reference to newly created controller
        c = context.object.game.controllers[-1]
        # configure appropriately
        c.mode = 'MODULE'
        c.module = 'pythonmocap.update'

    def createSensor(self, context):
        print('PyMoCap creating Always sensor')
        # create the sensor
        bpy.ops.logic.sensor_add(type='ALWAYS')
        # get reference to newly created sensor
        s = context.object.game.sensors[-1]
        s.use_pulse_true_level = True

# This class represents the config data (that the UI Panel interacts with)
class Config(bpy.types.PropertyGroup):
  @classmethod
  def register(cls):
    bpy.types.Object.pyMoCapConfig = bpy.props.PointerProperty(
      name="PyMoCap Config",
      description="Object-specific PyMoCap connection configuration",
      type=cls)

    # Add in the properties
    cls.enabled = bpy.props.BoolProperty(name="enabled", default=False, description="Enable PyMoCap")

# This class represents the config data (that the UI Panel interacts with)
class NatnetConfig(bpy.types.PropertyGroup):
  @classmethod
  def register(cls):
    bpy.types.Object.pyMoCapNatnetConfig = bpy.props.PointerProperty(
      name="PyMoCap Natnet Config",
      description="Object-specific PyMoCap Natnet connection configuration",
      type=cls)

    # Add in the properties
    cls.enabled = bpy.props.BoolProperty(name="enabled", default=False, description="Enable PyMoCap Natnet Receiver")
    cls.host = bpy.props.StringProperty(name="Host", default="0.0.0.0")
    cls.multicast = bpy.props.StringProperty(name="Multicast", default='239.255.42.99')
    cls.port = bpy.props.IntProperty(name="Port", default=1511, soft_min=0)

class NatnetFileConfig(bpy.types.PropertyGroup):
  @classmethod
  def register(cls):
    bpy.types.Object.pyMoCapNatnetFileConfig = bpy.props.PointerProperty(
      name="PyMoCap Natnet File Config",
      description="Object-specific PyMoCap connection configuration",
      type=cls)

    # Add in the properties
    cls.enabled = bpy.props.BoolProperty(name="enabled", default=False, description="Enable PyMoCap")
    cls.file = bpy.props.StringProperty(name="file", default="recording.binary", subtype="FILE_PATH")
    cls.loop = bpy.props.BoolProperty(name="loop", default=True, description="Loop back to start after reaching the end of mocap file")
    cls.sync = bpy.props.BoolProperty(name="sync", default=True, description="Synchronise mocap data using the embedded timestamps")

# This class represents the config data (that the UI Panel interacts with)
class RbFollowerConfig(bpy.types.PropertyGroup):
  @classmethod
  def register(cls):
    bpy.types.Object.pyMoCapRbFollowerConfig = bpy.props.PointerProperty(
      name="PyMoCap Spawner Config",
      description="Object-specific PyMoCap RbFollower configuration",
      type=cls)

    # Add in the properties
    cls.enabled = bpy.props.BoolProperty(name="enabled", default=False, description="Enable PyMoCap RigidBody Follower for this object")
    cls.rbid = bpy.props.IntProperty(name="Rigid Body Id", default=0, description="Id of rigid body to follow. 0 means disabled", soft_min=0)
    cls.rbindex = bpy.props.IntProperty(name="Rigid Body Index", default=-1, description="Index of rigid body to follow. -1 means diabled", soft_min=0)


# This class represents the config data (that the UI Panel interacts with)
class SpawnerConfig(bpy.types.PropertyGroup):
  @classmethod
  def register(cls):
    bpy.types.Object.pyMoCapSpawnerConfig = bpy.props.PointerProperty(
      name="PyMoCap Spawner Config",
      description="Object-specific PyMoCap Spawner configuration",
      type=cls)

    # Add in the properties
    cls.enabled = bpy.props.BoolProperty(name="enabled", default=False, description="Enable PyMoCap Spawner for this object")
    cls.object = bpy.props.StringProperty(name="object", default="", description="Object to spawn for every MoCap rigid body")

def register():
  bpy.utils.register_module(__name__)

def unregister():
  bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
  register()

setup()
