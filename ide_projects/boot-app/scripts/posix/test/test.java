import jklipper.utils.system.SystemDetector;
import org.apache.log4j.Logger;
import org.apache.log4j.*;
import jklipper.utils.*;

public class test {
	
	private static Logger log = Logger.getLogger(test.class);
	
	public static void main(String ... args)throws Exception{
		BasicConfigurator.configure();
		log.info("Welcom in test application ! ;~}");
		log.info("SysInfo:"+ SystemDetector.getSystemFullName());


		log.info("Usage:" +
			"\n\tFirst parameter describe number of ms to sleep before exit." +
			"\n\tSecond parameter is exitcode.");

		int nArgs = args.length;
		int exitcode =0;

		
		String sArgs = Utilities.toString(args);
		log.info("Hello word "+test.class.getSimpleName()+" args["+nArgs+"]:"+sArgs);
		
		if(nArgs>0){
			int sleep=Utilities.Numbers.parse(args[0],10);
			log.info("Internal: got to sleep "+sleep+"ms. ZzzZZZzzzZZZZzzZZzz...");
			Thread.sleep(sleep);
			
		}
		if(nArgs>1){
			exitcode =Utilities.Numbers.parse(args[1],0);
		}

		log.info("Application exit with exitcode:"+exitcode);
		System.exit(exitcode);
	}
}
