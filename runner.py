#!/usr/bin/env python3

import argparse
import logging
import signal
import subprocess
import sys
import threading


logger = logging.getLogger(__name__)

stop_flag = threading.Event()
signals_received = set()


def main():
    p = argparse.ArgumentParser()
    args = p.parse_args()
    setup_logging()
    setup_signals()
    try:
        with ProcessManager() as pm:
            pm.start_process(['redis-server', 'redis.conf'])
            pm.start_process(['node', 'server'], cwd='web')
            for i in range(10):
                pm.start_process(['./backend/rpc_worker.py', '--verbose'])
                if stop_flag.is_set():
                    logger.info('Stopped during startup')
                    break
            logger.info('All processes have started')
            pm.run()
        logger.info('Done')
    except Exception as e:
        sys.exit('ERROR: {}'.format(e))


class ProcessManager:

    def __init__(self):
        self.processes = []
        self.threads = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_all_processes()
        self.join_threads()

    def start_process(self, cmd, cwd=None):
        p = subprocess.Popen(
            cmd, cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        self.processes.append(p)
        logger.info('Started process %s pid %s', cmd, p.pid)
        self.threads.append(run_tail_thread('{pid}:'.format(pid=p.pid), p.stdout))
        self.check_all_processes_are_alive()

    def run(self):
        while True:
            stop_flag.wait(1)
            if stop_flag.is_set():
                logger.info('Stopping - signals received: %s', ' '.join(str(sig) for sig in signals_received))
                break
            self.check_all_processes_are_alive()

    def check_all_processes_are_alive(self):
        for p in self.processes:
            if p.poll() is not None:
                logger.error('Process %s has exited with returncode %s', p.pid, p.returncode)
                raise Exception('Process pid {} has exited'.format(p.pid))

    def stop_all_processes(self):
        alive = [p for p in self.processes if p.poll() is None]

        if signal.SIGINT not in signals_received:
            for p in alive:
                logger.info('Terminating process %s', p.pid)
                p.terminate()

        for p in alive:
            p.wait()
            logger.info('Process %s done with returncode %s', p.pid, p.returncode)

    def join_threads(self):
        '''
        Wait for all stdout "tail" threads to finish.
        But sometimes the process output is still not closed, so do not freeze on it.
        '''
        for t in self.threads:
            t.join(1)
            if t.is_alive():
                logger.warning('Thread %r did not join until timeout', t)


def setup_logging():
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.DEBUG)


def setup_signals():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def signal_handler(signum, frame):
    stop_flag.set()
    signals_received.add(signum)


def run_tail_thread(prefix, stream):
    def tail():
        while True:
            line = stream.readline()
            if not line:
                break
            try:
                line = line.decode()
            except Exception as e:
                line = str(line)
            logger.info('%s %s', prefix, line.rstrip())
    t = threading.Thread(target=tail)
    t.start()
    return t


if __name__ == '__main__':
    main()
