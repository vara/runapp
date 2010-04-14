import org.apache.log4j.Logger;
import org.apache.log4j.*;

public class test {
	
	private static Logger log = Logger.getLogger(test.class);
	
	public static void main(String ... args){
		BasicConfigurator.configure();
		
		String sArgs = jklipper.utils.Utilities.toString(args);
		log.info("Hello word "+test.class.getSimpleName()+" args:"+sArgs);
	}
}
