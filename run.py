from absl import app, flags, logging

from src.application import GetGameFlowUsecase

FLAGS = flags.FLAGS

# TODO help(third argument)
flags.DEFINE_string('mode', 'get_game_flow', '')
flags.DEFINE_string('input_file', None, '')


def main(_):
    if FLAGS.mode == 'get_game_flow':
        logging.info('Starting to get Game Flow.')
        get_game_flow_usecase = GetGameFlowUsecase(FLAGS.input_file)
        get_game_flow_usecase.run()


if __name__ == '__main__':
    app.run(main)
