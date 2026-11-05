pipeline {

  agent any



  triggers {

    pollSCM('H/2 * * * *')  // CI: revisa el repo cada ~2 min

    cron('H 7 * * 1-5')   // auditoría diaria, aunque nadie toque el código

  }



  environment {

    PIPENV_YES = '1'

    PIPENV_NOSPIN = '1'

    PIPENV_VERBOSITY = '-1'

  }



  stages {

    stage('Build') {

      steps {

        sh '''

          mkdir -p reports

          pipenv verify     # ¿el lock corresponde al Pipfile?

          pipenv sync --dev   # instala exactamente lo que dice el lock

        '''

      }

    }



    stage('Test') {

      steps {

        sh 'pipenv run python -m pytest -q --junitxml=reports/junit.xml'

      }

      post {

        always { junit 'reports/junit.xml' }

      }

    }



    stage('Analyze · SAST') {

      steps {

        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {

          sh 'bandit -r . -ll -x ./test_app.py'

        }

      }

    }



    stage('Dependency Management') {

      steps {

        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {

          sh '''

            pipenv graph > reports/arbol-dependencias.txt

            pipenv run pip list --outdated > reports/desactualizadas.txt

            pipenv requirements --hash > reports/lock-requirements.txt

            pip-audit -r reports/lock-requirements.txt --require-hashes --disable-pip \

              -f markdown -o reports/pip-audit.md || { cat reports/pip-audit.md; exit 1; }

          '''

        }

      }

    }



    stage('Deploy (staging)') {

      steps {

        sh '''

          # dontKillMe: que Jenkins no mate la app al terminar este paso

          JENKINS_NODE_COOKIE=dontKillMe nohup "$(pipenv --py)" app.py > reports/app.log 2>&1 &

          echo $! > app.pid

          sleep 4

          curl -fsS localhost:5000/health

        '''

      }

    }



    stage('Security Test · DAST') {

      steps {

        script {

          def rc = sh(script: 'zap.sh -cmd -port 8090 -autorun "$WORKSPACE/zap.yaml"', returnStatus: true)

          if (rc == 1) { error('ZAP encontró hallazgos de riesgo ALTO') }

          if (rc == 2) { unstable('ZAP encontró hallazgos de riesgo MEDIO') }

        }

      }

    }

  }



  post {

    always {

      sh 'if [ -f app.pid ]; then kill "$(cat app.pid)" || true; rm -f app.pid; fi'

      archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true

    }

    failure { echo "🔴 ALERTA: ${env.JOB_NAME} #${env.BUILD_NUMBER} bloqueado por seguridad: ${env.BUILD_URL}" }

    unstable { echo "🟡 AVISO: ${env.JOB_NAME} #${env.BUILD_NUMBER} con hallazgos medios: ${env.BUILD_URL}" }

    success { echo "🟢 ${env.JOB_NAME} #${env.BUILD_NUMBER} listo para producción" }

  }

}
